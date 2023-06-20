from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name='Электронная почта',
    )

    username = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True,
        validators=[UnicodeUsernameValidator, ]
    )

    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Имя',
        validators=[UnicodeUsernameValidator, ]
    )

    last_name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Фамилия',
        validators=[UnicodeUsernameValidator, ]
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('pk',)

    def __str__(self) -> str:
        return self.username
