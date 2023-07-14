from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import CreateAnyOtherAuthenticatedPermission
from api.serializers import SubscribeSerializer
from recipes.models import Recipe
from users.models import User, UserSubscribe
from users.pagination import CustomPagination
from users.serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [CreateAnyOtherAuthenticatedPermission]
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        subscriber = request.user
        target_user = get_object_or_404(User, id=id)
        subscribe_existence = UserSubscribe.objects.filter(
            subscriber=subscriber.id,
            target_user=target_user.id
        ).exists()

        if request.method == 'POST':
            if subscribe_existence:
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора'},
                    status=400
                )
            if subscriber == target_user:
                return Response(
                    {'errors': 'Подписываться на себя нельзя'},
                    status=400
                )
            subscription = UserSubscribe(
                subscriber=subscriber,
                target_user=target_user
            )
            subscription.save()
            serializer = SubscribeSerializer(
                target_user,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)

        if not subscribe_existence:
            return Response(
                {'errors': 'Вы не подписаны на данного автора'},
                status=400
            )
        subscription = UserSubscribe.objects.get(
            subscriber=subscriber,
            target_user=target_user
        )
        subscription.delete()
        return Response(status=204)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriber = request.user
        queryset = User.objects.filter(subscribers__subscriber=subscriber)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
