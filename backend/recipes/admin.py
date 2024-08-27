from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, ShortLink, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'favorite_count', 'get_ingredients',]
    search_fields = ['name', 'author__name']
    list_filter = ['tags']
    inlines = (IngredientInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorite_count=Count('favorites'))
        return queryset

    @admin.display(description='Число добавлений рецепта в избранное')
    def favorite_count(self, obj):
        return obj.favorite_count

    def get_ingredients(self, obj):
        return ', '.join([
            ingredients.name for ingredients
            in obj.ingredients.all()])

    get_ingredients.short_description = 'Ингредиенты'


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
