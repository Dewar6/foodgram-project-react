from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe
from users.models import User, UserSubscribe
from api.validators import validate_username



class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed',)


    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.subscribers.filter(subscriber=request.user).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        

class SubscribeSerializer(CustomUserSerializer):
    # recipe_count = SerializerMethodField()
    # recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields
        read_only_fields = (
            'email',
            'username'
        )

        # def validate(self, data):
        #     subscriber = self.instance
        #     target_user = self.context.get('request').user
        #     if UserSubscribe.objects.filter(
        #         subscriber=subscriber.id,
        #         target_user=target_user.id
        #     ).exists():
        #         raise ValidationError(
        #             detail='Вы уже подписаны на данного автора'
        #         )
        #     if target_user == subscriber:
        #         raise ValidationError(
        #             detail='Подписываться на себя нельзя'
        #         )
        #     return data






