import base64

from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import IntegrityError
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag,
                            UserSubscribe, IngredientAmount)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

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


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        read_only_fields = (
            'id',
            'name',
            'measurement_unit',            
        )

    def get_amount(self, obj):
        request = self.context.get('request')
        return request.data['amount']


    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context['view'].action == 'create':
            del data ['measurement_unit']
        return data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


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
    ingredients = IngredientSerializer(
        many=True
    )
    tags = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
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
        model = Recipe
        read_only_fields = (
            'is_favorited',
            'is_shopping_cart',
        )

    def create(self, validated_data):
        # print(validated_data)
        ingredients_data = validated_data.pop('ingredients')
        amount = validated_data.pop('amount')
        tags_data = validated_data.pop('tag', [])
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.create(amount=amount, **ingredient_data)
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient)
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

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return obj.is_favorited(user)

    def get_tags(self, obj):
        return obj.tags.values_list('id', flat=True)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return obj.is_in_shopping_cart(user)

    #def to_internal_value(self, data):
    #     data['image'] = 'Обработанное значение'
    #     return super().to_internal_value(data)


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


class SubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField(
        source='subscriber.email',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='subscriber.id',
        read_only=True
    )
    username = serializers.CharField(
        source='subscriber.username',
        read_only=True
    )
    first_name = serializers.CharField(
        source='subscriber.first_name',
        read_only=True
    )
    last_name = serializers.CharField(
        source='subscriber.last_name',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipe = serializers.SerializerMethodField()
    recipe_count = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscribe
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return UserSubscribe.objects.filter(subscriber=user).exists()

    def get_recipes(self, obj):
        user = self.context['request'].user
        subscribed = UserSubscribe.objects.filter(subscriber=user)
        subscribed_users = subscribed.values_list('target_user', flat=True)
        return Recipe.objects.filter(author__in=subscribed_users)

    def get_recipes_count(self, obj):
        user = self.context['request'].user
        subscribed = UserSubscribe.objects.filter(subscriber=user)
        subscribed_users = subscribed.values_list('target_user', flat=True)
        return Recipe.objects.filter(author__in=subscribed_users).count()

        
#class ProfileSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.BooleanField(
#         required=True,
#     )
#     username = serializers.CharField(
#         required=True,
#         max_length=150,
#         validators=[validate_username,
#         UniqueValidator(queryset=User.objects.all())]
#     )
#     email = serializers.EmailField(
#         required=True,
#         max_length=255,
#         validators=[UniqueValidator(queryset=User.objects.all())]
#     )

#     class Meta:
#         model = User
#         fields = (
#             'email',
#             'id',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed'
#         )

#     def get_is_subscribed(self, obj):
#         user = self.context['request'].user
#         return (
#             UserSubscription.objects.filter(subscriber=user).exists()
#             or FavoriteRecipe.objects.filter(user=user).exists()
#         )


#class SetPasswordSerializer(serializers.Serializer):
#     current_password = serializers.CharField(
#         required=True,
#         max_length=128
#     )
#     new_password = serializers.CharField(
#         required=True,
#         max_length=128
#     )

#     def validate_current_password(self, value):
#         user = self.context['request'].user
#         if not user.check_password(value):
#             raise serializers.ValidationError('Неверный текущий пароль')
#         return value