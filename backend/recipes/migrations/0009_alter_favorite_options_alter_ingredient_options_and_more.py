# Generated by Django 5.0.7 on 2024-08-26 06:45

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_shoppingcart_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'default_related_name': 'favorites', 'ordering': ['user'], 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранные'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name'], 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={'default_related_name': 'ingredient_recipe_set', 'ordering': ['recipe'], 'verbose_name': 'Ингредиент в рецепте', 'verbose_name_plural': 'Ингредиенты в рецепте'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes', 'ordering': ['-pub_date'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'default_related_name': 'shopping_carts', 'ordering': ['user'], 'verbose_name': 'Корзина', 'verbose_name_plural': 'Корзины'},
        ),
        migrations.AlterModelOptions(
            name='shortlink',
            options={'ordering': ['recipe'], 'verbose_name': 'Сокращенная ссылка', 'verbose_name_plural': 'Сокращенные ссылки'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['name'], 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favourite',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_shopping_cart',
        ),
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления (в минутах)'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='recipes.tag', verbose_name='Теги'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=150, unique=True),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite_user_recipe'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shoppingcart_user_recipe'),
        ),
    ]
