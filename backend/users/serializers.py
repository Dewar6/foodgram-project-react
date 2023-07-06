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
        return obj.subscribers.filter(target_user=obj.id).exists()


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
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (CustomUserSerializer.Meta.fields
                  + ('recipes', 'recipes_count',))

        read_only_fields = (
            'email',
            'username'
        )


    def get_recipes(self, obj):
        from api.serializers import SubscribeRecipeSerializer

        recipes = Recipe.objects.filter(author=obj.id)
        serializer = SubscribeRecipeSerializer(
            recipes,
            many = True,
            read_only = True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj.id)
        return recipes.count()