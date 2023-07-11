from django.core.exceptions import PermissionDenied

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag, TagRecipe)
from users.serializers import CustomUserSerializer


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


class IngredientAmountSerializer(IngredientSerializer):
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


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
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

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(min_value=1)

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
        ingredients_list = []

        for index in range(len(data['ingredients'])):
            amount = data['ingredients'][index]['amount']

            if amount < 1:
                raise serializers.ValidationError(
                    {'amount':
                    'Убедитесь, что это значение больше либо равно 1'}
                )

            if data['ingredients'][index]['id'] in ingredients_list:
                raise serializers.ValidationError(
                    {'error': 'Данный ингредиент уже добавлен'}
                )
            ingredients_list.append(data['ingredients'][index]['id'])

        if self.instance is not None:
            if self.instance.author != author:
                raise PermissionDenied
        else:
            if Recipe.objects.filter(author=author, name=name).exists():
                raise serializers.ValidationError(
                    {'error':
                     'Рецепт с таким названием уже существует у вас'}
                )

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
                amount=amount
            )
            ingredient_amount.save()

        for tag in tags:
            TagRecipe.objects.create(recipe=recipe, tag=tag)

        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientAmount.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        for ingredient in ingredients:
            print(ingredient)
            amount = ingredient['amount']
            ingredient_obj = Ingredient.objects.get(pk=ingredient['id'])
            ingredient_amount = IngredientAmount.objects.create(
                recipe=instance,
                ingredient=ingredient_obj,
                amount=amount
            )
            ingredient_amount.save()

        for tag in tags:
            TagRecipe.objects.create(recipe=instance, tag=tag)

        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class SubscribeFavoriteRecipeSerializer(serializers.ModelSerializer):

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


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
