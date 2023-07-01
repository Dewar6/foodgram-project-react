from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe
from users.models import UserSubscribe
from api.validators import validate_username


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed',)
        extra_kwargs = {
            'is_subscribed': {'read_only': True},
        }


    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.subscribers.filter(subscriber=request.user).exists()


    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context['view'].action == 'create':
            data = {
                'email': instance.email,
                'id': instance.id,
                'username': instance.username,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
            }
        return data


    def create(self, validated_data):
        try:
            user = User(
                email=validated_data["email"],
                username=validated_data["username"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
            )
            user.set_password(validated_data["password"])
            user.save()
        except IntegrityError:
            error_message = 'Пользователь с таким именем или адресом электронной почты уже существует.'
            raise serializers.ValidationError(error_message)
        return user


class SubscribeSerializer(serializers.ModelSerializer):
    recipe_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipe_count',
            'recipes'
        )
        read_only_fields = (
            'email',
            'username'
        )

        def validate(self, data):
            subscriber = self.instance
            target_user = self.context.get('request').user
            if UserSubscribe.objects.filter(
                subscriber=subscriber,
                target_user=target_user
            ).exists():
                raise ValidationError(
                    detail='Вы уже подписаны на данного автора'
                )
            if target_user == subscriber:
                raise ValidationError(
                    detail='Подписываться на себя нельзя'
                )
            return data






