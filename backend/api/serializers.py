import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import IntegrityError
from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from api.validators import validate_username

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username, ]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username, ]
    )
    confirmation_code = serializers.CharField(
        required=True,
    )


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username,
                    UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username,
        UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        max_length=255,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('role',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class ImageField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

    def to_representation(self, value):
        return value.url


class RecipeSerializer(serializers.ModelSerializer):
    image = ImageField()
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        many=True
    )
    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Recipe

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tag', [])
        recipe = super().create(validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        recipe.tag.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tag', [])
        instance = super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=instance, **ingredient_data)
        instance.tag.set(tags_data)
        return instance