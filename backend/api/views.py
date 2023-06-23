from http import HTTPStatus

from djoser.conf import settings as djoser_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets, serializers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import IngredientFilter
from api.permissions import (AdminOrReadOnlyPermission,
                             AuthorAndStaffOrReadOnlyPermission,
                             IsAdminOrSuperUser)
from api.serializers import (SignUpSerializer, TokenSerializer,
                             IngredientSerializer, UserWriteSerializer,
                             TagSerializer, RecipeSerializer,
                             ProfileSerializer, UserReadSerializer,
                             SetPasswordSerializer)
from foodgram_backend.settings import DEFAULT_FROM_EMAIL
from recipes.models import Ingredient, Tag, Recipe


User = get_user_model()


@api_view(['post'])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def sign_up(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')
    first_name = serializer.validated_data.get('first_name')
    last_name = serializer.validated_data.get('last_name')
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
    except IntegrityError:
        message = ('Пользователь с такими данными уже существует!')
        raise serializers.ValidationError(message)
    serializer = SignUpSerializer(user)
    return Response(serializer.data, status=HTTPStatus.OK)


@api_view(['post'])
@permission_classes([permissions.AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = get_object_or_404(User, email=email)
    if not user.check_password(password):
        return Response(
            {'error_message': 'Неверный пароль или адрес электронной почты'},
            status=HTTPStatus.BAD_REQUEST
        )
    token = default_token_generator.make_token(user)
    return Response(
        {'auth_token': token},
        status=HTTPStatus.OK
    )

@api_view(['post'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    user = request.user
    try:
        Token.objects.filter(user=user).delete()
    except Token.DoesNotExist:
        pass
    return Response(status=HTTPStatus.OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAdminOrSuperUser,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'set_password']:
            return UserWriteSerializer
        return UserReadSerializer

    @action(detail=True, methods=['get'])
    def user_info(self, request, pk=None):
        user = self.get_object()
        serializers = UserReadSerializer(user)
        return Response(serializers.data)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=ProfileSerializer
    )
    def profile_me(self, request):
        if request.method == 'PATCH':
            serializer = ProfileSerializer(
                self.request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data,
                status=HTTPStatus.OK
            )
        serializer = ProfileSerializer(self.request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password'
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Пароль успешно изменён'}, status=HTTPStatus.OK)


# class RecipeViesSet(viewsets.ModelViewSet):
#     queryset = Recipe.objects.all()
