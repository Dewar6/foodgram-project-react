from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets, serializers
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import (IsAuthenticatedOrReadOnly, AllowAny,
                                        IsAuthenticated)


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
                            FavoriteRecipe, UserSubscribe)


User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipesFilter


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientsFilter


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = UserSubscribe.objects.all
    serializer_class = SubscribeSerializer