from django.db import IntegrityError
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
                             ShoppingCartSerializer,
                             FavoriteRecipeSerializer,)
from recipes.models import (Ingredient, Tag, Recipe, ShoppingCart,
                            FavoriteRecipe)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer


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


