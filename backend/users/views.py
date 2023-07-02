from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from api.permissions import CreateAnyOtherAuthenticatedPermission
from users.models import User, UserSubscribe
from users.serializers import SubscribeSerializer, UserSerializer

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CreateAnyOtherAuthenticatedPermission,]


    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk):
        subscriber = request.user
        queryset = User.objects.all()
        print(list(queryset))
        target_user = get_object_or_404(User, id=pk)
        if UserSubscribe.objects.filter(subscriber=subscriber.id, target_user=target_user.id).exists():
            return Response({'message': 'Вы уже подписаны на данного автора'}, status=400)
        if subscriber == target_user:
            return Response({'message': 'Подписываться на себя нельзя'}, status=400)
        subscription = UserSubscribe(subscriber=subscriber, target_user=target_user)
        subscription.save()
        return Response({'message': 'Подписка создана'}, status=201)




    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    # )
    # def subscribe(self, request, pk):
    #     subscriber = request.user
    #     target_user = get_object_or_404(User, id=pk)
        
    #     if request.method == 'POST':
    #         serializer = SubscribeSerializer(
    #             target_user,
    #             data=request.data,
    #             context={'request': request}
    #         )
    #         serializer.is_valid(raise_exception=True)
    #         subscribe = UserSubscribe.objects.create(
    #             subscriber=subscriber,
    #             target_user=target_user
    #         )
    #         subscribe.save()
    #         return Response(serializer.data)

