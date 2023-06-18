from django.contrib import admin

from recipes.models import Recipe, Tag, Ingredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', )


admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)