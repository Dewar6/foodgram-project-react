from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import UserSubscribe
from users.serializers import SubscribeSerializer, UserSerializer


User = get_user_model()


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def subscribe(self, request, *args, **kwargs):
        subscriber = request.user
        target_user_id = self.kwargs.get('user_id')
        target_user = get_object_or_404(User, id=target_user_id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                target_user,
                data=request.data,
                context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        UserSubscribe.objects.create(
            subscriber=subscriber,
            target_user=target_user
        )
        return Response(serializer.data)

class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        user = self.request.user
        return UserSubscribe.objects.filter(subscriber=user)
    