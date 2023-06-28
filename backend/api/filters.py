from django_filters.rest_framework import FilterSet, CharFilter

from recipes.models import Ingredient, Recipe


class IngredientsFilter(FilterSet):
    starts_with_name = CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        label='Поиск по вхождению в начало названия'
    )
    contains_name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Поиск по вхождению в произвольном месте'
    )

    class Meta:
        models = Ingredient
        fields = '__all__'


class RecipesFilter(FilterSet):
    # favorite = 
    author = CharFilter(
        field_name='author',
        lookup_expr='icontains',
    )
    # shopping_list = 
    tag = CharFilter(
        field_name='tag__slug',
        lookup_expr='icontains',
    )

    class Meta:
        models = Recipe
        fields = '__all__'