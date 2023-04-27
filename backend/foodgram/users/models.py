from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    USER_ROLES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    role = models.CharField(
        max_length=9,
        choices=USER_ROLES,
        default=USER,
        verbose_name='Права доступа',
    )
    email = models.EmailField(
        max_length=256,
        blank=False,
        unique=True,
        verbose_name='Электронная почта',
    )

    password = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Пароль',
    )
    
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя',
    )

    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия',
    )

    
    is_subscribed = models.BooleanField(
        default = False,
        verbose_name='Подписка',
    )
    

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('pk',)

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

