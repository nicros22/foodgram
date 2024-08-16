from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError
from recipes.models import Tag, Ingredient, Recipe, IngredientRecipe, Favorite
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


class RecipeSerializerMixin(serializers.ModelSerializer):

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
        serializer = RecipeSerializerMixin(recipes, many=True, read_only=True)
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


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeInfoSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'cooking_time',
                  'text')

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return obj.shopping_cart.filter(user=user).exists()


class RecipeCreateSerializer(RecipeInfoSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientRecipeSerializer(many=True)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_id,
                amount=amount
            )
        return recipe

    def validate(self, data):
        if not data['tags']:
            raise ValidationError({'tags': 'This field is required.'})
        if not data['ingredients']:
            raise ValidationError({'ingredients': 'This field is required.'})
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

    def to_representation(self, instance):
        return RecipeSerializerMixin(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
