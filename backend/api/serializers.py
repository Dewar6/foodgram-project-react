import base64

from drf_extra_fields.fields import Base64ImageField
from django.core.files.base import ContentFile
from django.db import transaction, IntegrityError
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            ShoppingCart, Tag, IngredientAmount)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from users.serializers import  User, CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = (
            'id',
            'name',
            'measurement_unit',            
        )

    # def get_amount(self, obj):
    #     request = self.context.get('request')
    #     return request.data['amount']


    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     if self.context['view'].action == 'create':
    #         del data ['measurement_unit']
    #     return data

class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'amount',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__'



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
    image = Base64ImageField()
    ingredients = IngredientAmountSerializer(
        many=True,
        write_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorited',
            'is_shopping_cart',
        )

    @transaction.atomic
    def create(self, validated_data):
        try: 
            ingredients_data = validated_data.pop('ingredients')
            tags_data = validated_data.pop('tags', [])
            recipe = Recipe.objects.create(**validated_data)

            for ingredient_data in ingredients_data:
                ingredient_amount = IngredientAmount.objects.create(
                    recipe=recipe,
                    **ingredient_data
                )
                ingredient_amount.save()

            recipe.tags.set(tags_data)
        except IntegrityError:
            error_message = 'Рецепт с таким названием у данного' \
                            'пользователя уже существует'
            raise serializers.ValidationError(error_message)
        return recipe


    #def update(self, instance, validated_data):
    #     ingredients_data = validated_data.pop('ingredients', [])
    #     tags_data = validated_data.pop('tag', [])
    #     instance = super().update(instance, validated_data)
    #     IngredientAmount.objects.filter(recipe=instance).delete()
    #     for ingredient_data in ingredients_data:
    #         ingredient = Ingredient.objects.create(**ingredient_data)
    #         IngredientAmount.objects.create(
    #             recipe=instance,
    #             ingredient=ingredient,
    #             amount=ingredient_data['amount']
    #         )
    #     instance.tags.set(tags_data)
    #     return instance

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return obj.is_favorited(user)

    def get_tags(self, obj):
        return obj.tags.values_list('id', flat=True)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return obj.is_in_shopping_cart(user)


class ShoppingCartSerializer(serializers.Serializer):
    image = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def get_image(self, obj):
        recipe = obj.recipe
        serializers = RecipeSerializer(recipe)
        return serializers.data.get('image')

    def get_cooking_time(self, obj):
        recipe = obj.recipe
        serializers = RecipeSerializer(recipe)
        return serializers.data.get('cooking_time')


class FavoriteRecipeSerializer(serializers.Serializer):
    image = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteRecipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def get_image(self, obj):
        recipe = obj.recipe
        serializers = RecipeSerializer(recipe)
        return serializers.data.get('image')

    def get_cooking_time(self, obj):
        recipe = obj.recipe
        serializers = RecipeSerializer(recipe)
        return serializers.data.get('cooking_time')

