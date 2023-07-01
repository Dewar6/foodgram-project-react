from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import (RecipeViewSet, TagViewSet, IngredientsViewSet,
                       ShoppingCartViewSet, FavoriteViewSet,)

from users.views import SubscribeViewSet, SubscriptionListView

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'users/(?P<user_id>\d+)/subscribe',
                SubscribeViewSet, basename='subscribe')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingCartViewSet, basename='shopping_cart')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                FavoriteViewSet, basename='favorite')
# router.register(
#     r'users/subscriptions', SubscriptionListView, basename='subscription'
# )


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('users/subscriptions/', SubscriptionListView.as_view(), name='subscription'),
]
