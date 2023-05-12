from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from foodgram.settings import MAX_LENGTH_EMAIL, MAX_LENGTH_NAME


def validate_username(value):
    for symbol in ('!', '@', '#', '$', '%', '^',
                   '&', '*', '~', ':', ';', ',', '/'):
        if symbol in value:
            raise ValidationError(
                'Имя пользователя содержит недопустимые символы'
            )


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        blank=False,
        unique=True,
        verbose_name='Электронная почта',
    )

    username = models.CharField(
        blank=True,
        max_length=MAX_LENGTH_NAME,
        unique=True,
        validators=[validate_username]
    )

    first_name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        blank=False,
        verbose_name='Имя',
    )

    last_name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        blank=False,
        verbose_name='Фамилия',
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('pk',)

    def __str__(self) -> str:
        return self.username
