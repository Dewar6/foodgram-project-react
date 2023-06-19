from django.urls import include, path
from rest_framework.routers import DefaultRouter

from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
]
