from django.contrib import admin
from django.db.models import Count

from .models import Ingredient, Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ['name', 'author__name']
    list_filter = ['tags']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorite_count=Count('favorites'))
        return queryset

    def favorite_count(self, obj):
        return obj.favorite_count

    favorite_count.short_description = 'Число добавлений рецепта в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ['name']
