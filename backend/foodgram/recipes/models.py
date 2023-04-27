from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False
    )
    color = models.CharField(
        max_length=7,
        unique=True, 
        blank=False
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=False
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, blank=False)
    measurement_unit = models.CharField(max_length=200, blank=False)

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name 
    

class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipes',
        verbose_name='ингридиент')
    
    tags = models.ManyToManyField(
        Tag, 
        through='TagRecipe', 
        verbose_name='тег'
    )
    
    image = models.ImageField(
        upload_to='recipes/', 
        null=True,  
        default=None
    )
    
    name = models.CharField(max_length=16)
    text = models.TextField()
    cooking_time = models.IntegerField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name 


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class IngredientRecipes(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient_recipes')
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
    )

    class Meta:
        ordering = ('-subscribing',)

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'],
                name='unique_subscription',
            )
        ]

class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_is_favourite',
    )
    
    class Meta:
        ordering = ('recipe',)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shopping_cart'
    )