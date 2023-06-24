from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from recipes.validators import validate_name


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL_USER,
        unique=True,
        verbose_name='Электронная почта',
    )

    username = models.CharField(
        max_length=settings.MAX_LENGTH_NAME_USER,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[UnicodeUsernameValidator()]
    )

    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME_USER,
        verbose_name='Имя',
        validators=[validate_name]
    )

    last_name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME_USER,
        verbose_name='Фамилия',
        validators=[validate_name]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username
