from api.validators import color_validator
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class IngredientQuantity(models.Model):
    name = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Выберите единицу измерения ингредиента',
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Ингредиент',
        help_text='Введите название ингредиента',
        blank=False,
        null=False,
        db_index=True,
    )

    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Единица измерения',
        help_text='Выберите единицу измерения ингредиента',
        blank=False,
        null=False,
    )
    quantity = models.ForeignKey(
        IngredientQuantity,
        on_delete=models.CASCADE,
        verbose_name='Количество',
        null=True,
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Тэг',
        help_text='Введите название тэга',
        blank=False,
        null=False,
        db_index=True,
    )

    color_code = models.CharField(
        max_length=7,
        validators=[color_validator],
        blank=False,
        null=False,
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Страница тега',
        help_text=('Введите адрес страницы тэга'),
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipe',
        blank=False,
        null=False,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        help_text='Введите название рецепта',
        max_length=255,
        blank=False,
        null=False,
        db_index=True,
    )
    image = models.ImageField(
        verbose_name='Фотографии блюда',
        help_text='Загрузите фотографии блюда',
        upload_to='images/',
        blank=False,
        null=False,    
    )
    text = models.TextField(
        verbose_name='Рецепт приготовления',
        help_text='Напишите рецепт приготовления блюда',
        blank=False,
        null=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты и их количество',
        through='RecipeIngredient',
        blank=False,
        null=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        help_text='Выберите тэги',
        #through='TagRecipe',
        blank=False,
        null=False,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления блюда (мин)',
        help_text='Введите время приготовления блюда',
        blank=False,
        null=False,
    )

    class Meta:
        unique_together = ('author', 'name')

    def __str__(self):
        return self.name

    def get_favorite_count(self):
        return self.favorite_recipe.count()
    get_favorite_count.short_description = 'Число добавлений в избранное'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )


class UserSubscribe(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        unique_together = ['subscriber', 'target_user']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        null=False,
        blank=False,
    )


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Список покупок',
        blank=False,
        null=False,
    )
    image = models.ImageField(
        verbose_name='Фотография блюда',
        upload_to='images/',
        blank=False,
        null=False,    
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда',
        null=False,
        blank=False,
    )
