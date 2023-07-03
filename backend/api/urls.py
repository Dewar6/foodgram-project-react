from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import (RecipeViewSet, TagViewSet, IngredientsViewSet,
                       ShoppingCartViewSet, FavoriteViewSet,)

from users.views import CustomUserViewSet


app_name = 'api'

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
