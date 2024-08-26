from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (LINK_MAX_LENGTH, MEASUREMENT_UNIT_MAX_LENGTH,
                               MIN_POSITIVE_VALUE, NAME_MAX_LENGTH,
                               RECIPE_NAME_MAX_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            db_index=True)
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               verbose_name='Автор рецепта',
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGTH)
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Изображение',
                              null=True,
                              default='')
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField('Tag',
                                  verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_POSITIVE_VALUE)],
        verbose_name='Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        default_related_name = 'recipes'
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    slug = models.SlugField(max_length=NAME_MAX_LENGTH,
                            unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class UserRecipeBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил рецепт "{self.recipe}"'


class Favorite(UserRecipeBase):
    class Meta(UserRecipeBase.Meta):
        ordering = ['user']
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            ),
        )


class ShoppingCart(UserRecipeBase):
    class Meta(UserRecipeBase.Meta):
        ordering = ['user']
        default_related_name = 'shopping_carts'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shoppingcart_user_recipe'
            ),
        )


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_POSITIVE_VALUE)],
        verbose_name='Количество')

    class Meta:
        ordering = ['recipe']
        default_related_name = 'ingredient_recipe_set'
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (f'{self.ingredient} в рецепте "{self.recipe}'
                f'в количестве {self.amount})')


class ShortLink(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    link = models.CharField(max_length=LINK_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Сокращенная ссылка'
        verbose_name_plural = 'Сокращенные ссылки'

    def __str__(self):
        return self.link
