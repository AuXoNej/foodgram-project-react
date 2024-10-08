from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .validators import validate_color, validate_name


User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME_TAG,
        unique=True,
        validators=[validate_name],
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=settings.MAX_LENGTH_COLOR_TAG,
        unique=True,
        validators=[validate_color],
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=settings.MAX_LENGTH_SLUG_TAG,
        unique=True,
        verbose_name='Слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME_INGREDIENT,
        validators=[validate_name],
        verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGTH_MEASUREMENT_UNIT_INGREDIENT,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            ),
        ]
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта'
    )

    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        default=None,
        verbose_name='Изображение'
    )

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME_RECIPE,
        validators=[validate_name],
        verbose_name='Название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(settings.MIN_COOKING_TIME)
        ],
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Модель ингридиентов рецепта."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Ингридиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(settings.MIN_AMOUNT)
        ],
        verbose_name='Величина'
    )

    def __str__(self):
        return self.ingredient.name


class Subscription(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь'
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Подписка',
        help_text='На кого подписан пользователь'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'], name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscribing')),
                name='Check_user',
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-subscribing',)


class Favourite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_is_favourite',
        verbose_name='Рецепт',
        help_text='Рецепт в избранном у пользователя'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favourite'
            ),
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('recipe',)


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shopping_cart',
        verbose_name='Рецепт',
        help_text='Рецепт в списке покупок у пользователя'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            ),
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('recipe',)
