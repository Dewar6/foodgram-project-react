from django.db import IntegrityError
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets, serializers, generics, status
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import (IsAuthenticatedOrReadOnly, AllowAny,
                                        IsAuthenticated)
from rest_framework.response import Response


from api.filters import IngredientsFilter, RecipesFilter
from api.permissions import (AdminOrReadOnlyPermission,
                             AuthorAndStaffOrReadOnlyPermission,
                             IsAdminOrSuperUser,
                             CreateAnyOtherAuthenticatedPermission)
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer, RecipeCreateSerializer,
                             ShoppingCartSerializer, FavoriteSerializer, 
                             SubscribeFavoriteRecipeSerializer)
from recipes.models import (Ingredient, IngredientAmount, Tag, Recipe,
                            ShoppingCart, FavoriteRecipe)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = RecipesFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-pub_date')
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=('POST', 'DELETE')
    )
    def favorite(self, request, pk):
        recipe = Recipe.objects.get(id=pk)
        user = request.user
        favorite_exists = FavoriteRecipe.objects.filter(
            user = user,
            recipe = recipe
        ).exists()

        if request.method == 'POST':

            if favorite_exists:
                return Response('Данный рецепт у вас уже в избранном',
                                status=status.HTTP_400_BAD_REQUEST)

            FavoriteRecipe.objects.create(
                user = user,
                recipe = recipe
            )
            serializer = SubscribeFavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':

            if not favorite_exists:
                return Response('Данного рецепта нет у вас в избранном',
                                status=status.HTTP_400_BAD_REQUEST)

            FavoriteRecipe.objects.filter(
                user = user,
                recipe = recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',))
    def favorites(self, request):
        user = request.user
        print(request.user)
        favorites = FavoriteRecipe.objects.filter(user=user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('POST', 'DELETE')
    )
    def shopping_cart(self, request, pk):
        recipe = Recipe.objects.get(id=pk)
        user = request.user
        shopping_cart_exists = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':

            if shopping_cart_exists:
                return Response('Данный рецепт уже в списке покупок',
                                status=status.HTTP_400_BAD_REQUEST)
        
            ShoppingCart.objects.create(
                user = user,
                recipe = recipe
            )
            serializer = SubscribeFavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':

            if not shopping_cart_exists:
                return Response('Данного рецепта нет у вас в списке покупок')

            ShoppingCart.objects.filter(
                user = user,
                recipe = recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',)
    )
    def download_shopping_cart(self, request):
        user = request.user
        queryset = ShoppingCart.objects.filter(user=user)
        ingredients_result = []

        for obj in queryset:
            recipe = Recipe.objects.get(id=obj.recipe.id)
            ingredients = IngredientAmount.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                amount = ingredient.amount
                measurement_unit = ingredient.ingredient.measurement_unit
                if len(ingredients_result) == 0:
                    ingredients_result.append([
                        name,
                        amount,
                        measurement_unit
                    ])
                else:
                    flag = False
                    for objs in ingredients_result: 
                        if name == objs[0]:
                            objs[1] += amount
                            flag = True
                            break
                    if not flag:
                        ingredients_result.append([
                            name,
                            amount,
                            measurement_unit
                        ])

        shopping_cart = 'Список покупок:\n'
        for item in ingredients_result:
            shopping_cart += f'{item[0]} - {item[1]} {item[2]}\n'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename=shopping_cart.txt'
        return response

class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientsFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)
