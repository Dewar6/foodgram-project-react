from api.validators import color_validator
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Ingredient(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Ингредиент',
        help_text='Название ингредиента',
        blank=False,
        null=False,
        db_index=True,
    )

    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Единица измерения',
        help_text='Eдиницу измерения ингредиента',
        blank=False,
        null=False,
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
        through='IngredientAmount',
        blank=False,
        null=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        help_text='Выберите тэги',
        through='TagRecipe',
        blank=False,
        null=False,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления блюда (мин)',
        help_text='Введите время приготовления блюда',
        blank=False,
        null=False,
    )
    favorite_recipes = models.ManyToManyField(
        User,
        through='FavoriteRecipe',
        related_name='favorite_recipes',
        blank=True,
        null=True,
    )
    in_shopping_cart = models.ManyToManyField(
        'recipes.ShoppingCart',
        related_name='recipes_in_shopping_cart',
        blank=True,
        null=True,
    )

    class Meta:
        unique_together = ('author', 'name')

    def __str__(self):
        return self.name

    def get_favorite_count(self):
        return self.favorite_by.count()
    get_favorite_count.short_description = 'Число добавлений в избранное'

    def is_favorited(self, user):
        return self.favorite_recipes.filter(id=user.id).exists()

    def is_in_shopping_cart(self, user):
        return self.shopping_cart_recipes.filter(recipe=self, user=user).exists()


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        blank=False,
        null=False
        
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество ингредиента',
    )

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite_recipes_favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite_by'
    )

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes'
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


#class RecipeIngredient(models.Model):
#     recipe = models.ForeignKey(
#         Recipe,
#         verbose_name='Рецепт',
#         on_delete=models.CASCADE,
#     )
#     ingredient = models.ForeignKey(
#         Ingredient,
#         verbose_name='Ингредиент',
#         on_delete=models.CASCADE
#     )
#     amount = models.PositiveSmallIntegerField(
#         verbose_name='Количество',
#         null=False,
#         blank=False,
#     )