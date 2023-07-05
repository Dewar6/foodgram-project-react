# Generated by Django 3.2.3 on 2023-07-05 09:50

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Название ингредиента', max_length=255, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(help_text='Eдиницу измерения ингредиента', max_length=10, verbose_name='Единица измерения')),
            ],
        ),
        migrations.CreateModel(
            name='IngredientAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(help_text='Укажите количество ингредиента', verbose_name='Количество')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Введите название рецепта', max_length=255, verbose_name='Название рецепта')),
                ('image', models.ImageField(help_text='Загрузите фотографии блюда', upload_to='images/', verbose_name='Фотографии блюда')),
                ('text', models.TextField(help_text='Напишите рецепт приготовления блюда', verbose_name='Рецепт приготовления')),
                ('cooking_time', models.PositiveIntegerField(help_text='Введите время приготовления блюда', verbose_name='Время приготовления блюда (мин)')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Введите название тэга', max_length=256, verbose_name='Тэг')),
                ('color', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(message='Цветовой код должен быть в формате HEX (например, #FFFFFF).', regex='^#[A-Fa-f0-9]{6}$')])),
                ('slug', models.SlugField(help_text='Введите адрес страницы тэга', unique=True, verbose_name='Страница тега')),
            ],
        ),
        migrations.CreateModel(
            name='TagRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.tag', verbose_name='Тэг')),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe')),
            ],
        ),
    ]
