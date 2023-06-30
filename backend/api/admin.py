from django import forms

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

from recipes.models import Recipe, Tag, Ingredient, IngredientAmount


class CustomUserAdmin(UserAdmin):
    search_fields = ('email', 'username')


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    verbose_name_plural = 'Ингредиенты'
    fields = ['ingredient', 'amount']


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=FilteredSelectMultiple('тэги', is_stacked=False),
        required=False
    )

    class Meta:
        model = Recipe
        fields = '__all__'

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code', 'slug',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ('name', 'author',)
    search_fields = ('author', 'name', 'tag',)
    readonly_fields = ('get_favorite_count',)
    form = RecipeForm
    filter_horizontal = ('tags',)

    def get_favorite_count(self, obj):
        return obj.favorite_recipe.count()
    get_favorite_count.short_description = 'Число добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)