from rest_framework import serializers
from django.contrib.auth.models import User

from recipes.models import Tag, Ingredient, Recipe


class UserSerializer(serializers.ModelSerializer):
    model = User
    fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserCreateSerializer(serializers.ModelSerializer):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name', 'password']
    extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class TagSerializer(serializers.ModelSerializer):
    model = Tag
    fields = ['id', 'title', 'slug']