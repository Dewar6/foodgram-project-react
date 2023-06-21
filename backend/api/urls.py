from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (sign_up, token, logout, UserViewSet)

app_name = 'api'

router = DefaultRouter()
# router.register(r'recipes', RecipeViewSet)
router.register(r'users', UserViewSet, basename='users')

auth_path = [
    path('users/', sign_up, name='signup'),
    path('auth/token/login/', token, name='token'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('', include(auth_path)),
]
