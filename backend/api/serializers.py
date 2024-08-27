from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.utils.base64_avatar_converter import Base64AvatarConverter
from recipes.constants import COOKING_TIME_LIMIT, MAX_AMOUNT_LIMIT
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'avatar', 'is_subscribed')

    def get_avatar(self, obj):
        return obj.avatar.url if obj.avatar else None

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.follower.filter(author=obj).exists())


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        required_fields = ['username', 'email', 'first_name',
                           'last_name', 'password']
        for field in required_fields:
            if field not in data:
                raise ValidationError({field: "This field is required."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class TokenCreateSerializer(serializers.ModelSerializer):

    class Meta:
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


class RecipeBaseSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)

    def get_image(self, obj):
        return obj.image.url if obj.image else None

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        limit = int(limit) if limit and limit.isdigit() else None
        recipes = recipes[:limit]
        serializer = RecipeBaseSerializer(recipes, many=True,
                                          context=self.context)
        return serializer.data


class SubscribeActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']
        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError("You are already following this user.")
        if user == author:
            raise ValidationError("You cannot subscribe to yourself.")
        return data

    def to_representation(self, instance):
        return SubscribeSerializer(instance.author, context=self.context).data


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, amount):
        if amount < MAX_AMOUNT_LIMIT:
            raise serializers.ValidationError(
                f'Количество ингредиента должно быть больше {MAX_AMOUNT_LIMIT}'
            )
        return amount


class RecipeInfoSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='ingredient_recipe_set')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(required=False)

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

    def get_image(self, obj):
        return obj.image.url if obj.image else ""

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.favorites.filter(user=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.shopping_carts.filter(user=request.user).exists())


class RecipeCreateSerializer(RecipeInfoSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientRecipeSerializer(many=True,
                                             required=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()
    text = serializers.CharField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time',)

    def set_ingredients(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                ingredient=ingredient['ingredient'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.set_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeInfoSerializer(instance, context=self.context).data

    def validate_text(self, text):
        if not text:
            raise serializers.ValidationError(
                'Отсутствует описание'
            )
        return text

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Отсутствуют изображения'
            )
        return image

    def validate_cooking_time(self, cooking_time):
        if cooking_time < COOKING_TIME_LIMIT:
            raise serializers.ValidationError(
                'Время готовки должно быть не меньше'
                f'{COOKING_TIME_LIMIT} минуты')
        return cooking_time

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Отсутствуют теги'
            )
        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                'Тэги не уникальны')
        return tags

    def validate(self, value):
        if (
                not value.get('ingredients') or not value.get('tags')
                or not value.get('name') or not value.get('text')
        ):
            raise serializers.ValidationError(
                'Отсутствует обязательное поле'
            )
        ingredients = value.get('ingredients')
        ingredient_ids = [ingredient['ingredient'].id
                          for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны'
            )
        return value


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    def validate(self, data):
        user = data['user']
        if self.Meta.model.objects.filter(user=user,
                                          recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
                if self.Meta.model == Favorite
                else 'Рецепт уже добавлен в корзину.'
            )
        return data

    def to_representation(self, instance):
        return RecipeBaseSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(BaseRecipeActionSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(BaseRecipeActionSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
