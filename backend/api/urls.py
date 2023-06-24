from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (UserViewSet)

app_name = 'api'

router = DefaultRouter()
# router.register(r'recipes', RecipeViewSet)
router.register(r'users', UserViewSet, basename='users')

#auth_path = [
#     path('auth/token/login/', token, name='token'),
# ]

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
