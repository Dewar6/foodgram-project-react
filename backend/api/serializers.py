import base64

from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from django.core.files.base import ContentFile
from django.db import transaction, IntegrityError
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            ShoppingCart, Tag, TagRecipe, IngredientAmount)
from rest_framework import serializers, status
from rest_framework.relations import SlugRelatedField
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from users.serializers import  User, CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):

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


    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     if self.context['view'].action == 'create':
    #         del data ['measurement_unit']
    #     return data

class IngredientAmountSerializer(IngredientSerializer):
    # id = serializers.PrimaryKeyRelatedField(
    #     queryset=Ingredient.objects.all(),
    # )
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'amount'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        # read_only_fields = '__all__'


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
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(ingredients, many=True).data

    
class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        author = self.context['request'].user
        name = data.get('name')
        try:
            Recipe.objects.get(author=author, name=name)
            raise serializers.ValidationError(
                {'error':
                'Рецепт с таким названием уже существует у данного автора'}
            )
        except Recipe.DoesNotExist:
            ingredients = self.initial_data.get('ingredients')
            ingredient_objects = []
            for ingredient in ingredients:
                ingredient = get_object_or_404(Ingredient,
                                            id=ingredient['id'])
                ingredient_objects.append(ingredient)
            data['ingredients'] = ingredients
            return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )

        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient_obj = Ingredient.objects.get(pk=ingredient['id'])
            ingredient_amount = IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount = amount
            )
            ingredient_amount.save()

        for tag in tags:
            TagRecipe.objects.create(recipe=recipe, tag=tag)
            
        recipe.tags.set(tags)
        return recipe

    # def update(self, instance, validated_data):
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
    

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request' : self.context.get('request')}
        ).data

class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )



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

