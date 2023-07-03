from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.permissions import CreateAnyOtherAuthenticatedPermission
from users.models import User, UserSubscribe
from users.serializers import SubscribeSerializer, CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [CreateAnyOtherAuthenticatedPermission,]


    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id):
        subscriber = request.user
        target_user = get_object_or_404(User, id=id)
        subscribe_existence = UserSubscribe.objects.filter(
            subscriber=subscriber.id,
            target_user=target_user.id    
        ).exists()

        if request.method == 'POST':
            if subscribe_existence is True:
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
            return Response({'message': 'Подписка создана'}, status=201)

        if request.method == 'DELETE':
            if subscribe_existence is not True:
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


    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        subscriber = request.user
        queryset = User.objects.filter(subscribers__subscriber=subscriber)
        serializer = SubscribeSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


