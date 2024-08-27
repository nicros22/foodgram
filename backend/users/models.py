from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.constants import MAIL_MAX_LENGTH, NAME_MAX_LENGTH
from users.validators import username_validator, validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    email = models.EmailField(
        'email address',
        max_length=MAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        validators=[validate_username, username_validator],
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        null=True,
        blank=True)

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['user']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'"{self.user}" добавил в подписки "{self.author}"'
