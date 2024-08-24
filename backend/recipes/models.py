from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               verbose_name='Автор рецепта',
                               related_name='recipes',
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField('Tag',
                                  verbose_name='Теги',
                                  related_name='recipes')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил рецепт "{self.recipe}" в избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_cart')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил рецепт "{self.recipe}" в корзину'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество')

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (f'{self.ingredient} в рецепте "{self.recipe}'
                f'в количестве {self.amount})')


class ShortLink(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    link = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name = 'Сокращенная ссылка'
        verbose_name_plural = 'Сокращенные ссылки'

    def __str__(self):
        return self.link
