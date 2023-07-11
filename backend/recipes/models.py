from api.validators import color_validator
from django.db import models
from users.models import User


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
        verbose_name='Тег',
        help_text='Введите название тега',
        blank=False,
        null=False,
        db_index=True,
    )

    color = models.CharField(
        max_length=7,
        validators=[color_validator],
        blank=False,
        null=False,
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Страница тега',
        help_text=('Введите адрес страницы тега'),
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
        blank=False,
        null=False,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        help_text='Введите название рецепта',
        max_length=200,
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
        blank=False,
        null=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда (мин)',
        help_text='Введите время приготовления блюда',
        blank=False,
        null=False,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_recipe'
            )
        ]

    def __str__(self):
        return self.name

    def get_favorite_count(self):
        favorite_count = FavoriteRecipe.objects.filter(recipe=self).count()
        print(self)
        return favorite_count
    get_favorite_count.short_description = 'Число добавлений в избранное'


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
        return (
            f'{self.ingredient} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


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
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_ShoppingCart'
            )
        ]

    def __str__(self):
        return (f'рецепт {self.recipe} в списке покупок '
                f'пользователя {self.user}')
