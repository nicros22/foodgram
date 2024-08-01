from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(User)
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


class Tag(models.Model):
    title = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)


class Ingredient(models.Model):
    title = models.CharField(max_length=256)
    unit = models.CharField(max_length=64)

