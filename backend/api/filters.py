from django_filters.rest_framework import FilterSet, CharFilter

from recipes.models import Ingredient


class IngredientFilter(FilterSet):
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