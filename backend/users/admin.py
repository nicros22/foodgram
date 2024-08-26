from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = ['username', 'email']
    list_display = ['username', 'email', 'recipe_count', 'follower_count']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            recipe_count=Count('recipes'),
            follower_count=Count('following')
        )
        return queryset

    @admin.display(description='Number of Recipes')
    def recipe_count(self, obj):
        return obj.recipe_count

    @admin.display(description='Number of Followers')
    def follower_count(self, obj):
        return obj.follower_count
