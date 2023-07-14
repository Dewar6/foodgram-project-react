from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import (status, viewsets)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.filters import IngredientsFilter, RecipesFilter
from api.permissions import AuthorAndStaffOrReadOnlyPermission
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             SubscribeFavoriteRecipeSerializer,
                             TagSerializer)
from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          AuthorAndStaffOrReadOnlyPermission,)
    filterset_class = RecipesFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-pub_date')
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    def favorite_shopping_cart_creator(self, model, request, pk):
        recipe = Recipe.objects.get(id=pk)
        user = request.user
        objects_exists = model.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':

            if objects_exists:
                return Response(
                    {'errors': 'Данный рецепт уже добавлен'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            model.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = SubscribeFavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not objects_exists:
            return Response(
                {'errors': 'Данного рецепта нет в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )

        model.objects.filter(
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
    )
    def favorite(self, request, pk):
        return self.favorite_shopping_cart_creator(FavoriteRecipe, request,
                                                   pk)

    @action(detail=False, methods=('GET',))
    def favorites(self, request):
        user = request.user
        favorites = FavoriteRecipe.objects.filter(user=user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('POST', 'DELETE')
    )
    def shopping_cart(self, request, pk):
        return self.favorite_shopping_cart_creator(ShoppingCart, request, pk)

    @action(
        detail=False,
        methods=('GET',)
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipe_ids = ShoppingCart.objects.filter(
            user=user).values_list('recipe_id', flat=True)
        ingredients = IngredientAmount.objects.filter(
            recipe_id__in=recipe_ids
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_cart = 'Список покупок:\n'
        for item in ingredients:
            name, measurement_unit, amount = item
            shopping_cart += f'{name} - {amount} {measurement_unit}\n'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt')
        return response


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientsFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
