from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets, serializers
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
                             RecipeSerializer, ShoppingCartSerializer,
                             FavoriteRecipeSerializer,
                             SubscribeSerializer)
from recipes.models import (Ingredient, Tag, Recipe, ShoppingCart,
                            FavoriteRecipe)

from users.models import UserSubscribe


User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipesFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     recipe = serializer.save(author=request.user)
    #     image = request.data.get('image')
    #     recipe.image.save(image.name, image, save=True)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data)

    # def perform_create(self, serializer):
    #     amount = self.request.data.get('amount')
    #     serializer.save(amount=amount)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientsFilter


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def create(self, request, *args, **kwargs):
        recipe_id = request.data.get('recipe_id')
        shopping_cart = ShoppingCart.objects.create()
        recipe = Recipe.objects.get(id=recipe_id)
        shopping_cart.recipe.add(recipe)
        serializers = self.get_serializer(shopping_cart)
        headers = self.get_success_headers(serializers.data)
        return Response(serializers.data, headers=headers)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = UserSubscribe.objects.all
    serializer_class = SubscribeSerializer