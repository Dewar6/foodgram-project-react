from django.contrib import admin

from recipes.models import Recipe, Tag, Ingredient, IngredientRecipe

class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    verbose_name_plural = 'Ингредиенты'
    fields = ['ingredient', 'quantity']

class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInline]

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)