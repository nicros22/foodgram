from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError
from recipes.models import Tag, Ingredient, Recipe
from .utils.base64_avatar_converter import Base64AvatarConverter
from rest_framework.fields import SerializerMethodField
from users.models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True, default=False)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Follow.objects.filter(user=request.user, author=obj).exists()
        return False

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'is_subscribed')


class UserCreateSerializer(serializers.ModelSerializer):

    def validate(self, data):
        required_fields = ['username', 'email', 'first_name', 'last_name', 'password']
        for field in required_fields:
            if field not in data:
                raise ValidationError({field: "This field is required."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class TokenCreateSerializer(serializers.ModelSerializer):
    model = User
    fields = ['email', 'password']
    extra_kwargs = {'password': {'write_only': True}}


class UserAvatarSetSerializer(serializers.ModelSerializer):
    avatar = Base64AvatarConverter()

    def to_representation(self, instance):
        return {'avatar': instance.avatar.url}

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def validate(self, data):
        user = self.context.get('request').user
        if Follow.objects.filter(user=user, author=self.instance).exists():
            raise ValidationError(
                detail='You are already following this user.',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == self.instance:
            raise ValidationError(
                detail='You cannot subscribe to yourself.',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
