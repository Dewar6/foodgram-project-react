from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientsFilter(FilterSet):
    starts_with_name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        label='Поиск по вхождению в начало названия'
    )
    contains_name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Поиск по вхождению в произвольном месте'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
        )

