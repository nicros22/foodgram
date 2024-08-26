from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Count

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, ShortLink, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ['name', 'author__name']
    list_filter = ['tags']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorite_count=Count('favorites'))
        return queryset

    @admin.display(description='Число добавлений рецепта в избранное')
    def favorite_count(self, obj):
        return obj.favorite_count

    def save_model(self, request, obj, form, change):
        if not obj.ingredients.exists():
            raise ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент.'
            )
        if not obj.tags.exists():
            raise ValidationError('Рецепт должен содержать хотя бы один тег.')
        super().save_model(request, obj, form, change)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'recipe__name']
    list_filter = ['user', 'recipe']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'recipe__name']
    list_filter = ['user', 'recipe']


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    search_fields = ['ingredient__name', 'recipe__name']
    list_filter = ['ingredient', 'recipe']


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    search_fields = ['link', 'recipe__name']
    list_filter = ['recipe']
