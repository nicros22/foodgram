from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag',
                                  verbose_name='Теги',
                                  related_name='recipes')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (в минутах)'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField(max_length=256)
    unit = models.CharField(max_length=64)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.title


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

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


# class User(AbstractUser):
#     """Базовая модель пользователей."""
#
#     email = models.EmailField(unique=True,
#                               verbose_name='Email',
#                               max_length=MAX_LENGTH_EMAIL)
#     bio = models.TextField(blank=True, verbose_name='О себе')
#     role = models.CharField(max_length=MAX_LENGTH_MODEL,
#                             choices=ROLE_CHOICES,
#                             default='user',
#                             verbose_name='Роль')
#
#     class Meta:
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'
#         ordering = ('username',)
#
#     def __str__(self):
#         return self.username
#
#     @property
#     def is_moderator(self):
#         return self.role == 'moderator'
#
#     @property
#     def is_admin(self):
#         return self.role == 'admin'
#
#     def clean(self):
#         if self.username.lower() == 'me':
#             raise ValidationError('Username "me" is not allowed.')

