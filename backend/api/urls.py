from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import (RecipeViewSet, TagViewSet, IngredientsViewSet,
                       ShoppingCartViewSet, FavoriteViewSet,
                       SubscribeViewSet)


app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'users/(?P<users_id>\d+)/subscribe',
                SubscribeViewSet, basename='subscribe')
router.register(r'recipes/(?P<recipes_id>\d+)/shopping_cart',
                ShoppingCartViewSet, basename='shopping_cart')
router.register(r'recipes/(?P<recipes_id>\d+)/favorite',
                FavoriteViewSet, basename='favorite')



urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
