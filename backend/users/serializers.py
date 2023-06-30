from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers

from users.models import UserSubscribe
from api.validators import validate_username


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.CharField(
        required=True,
        max_length=150,
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )
    password = serializers.CharField(
        required=True,
        max_length=128,
        write_only=True,
    )
    first_name = serializers.CharField(
        required=True,
        max_length=150,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=150
    )
    id = serializers.IntegerField(
        required=False
    )

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
        if self.context['request'].method == 'GET':
            user = self.context['request'].user
            return UserSubscribe.objects.filter(subscriber=user).exists()
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context['view'].action == 'create':
            del data['is_subscribed']
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