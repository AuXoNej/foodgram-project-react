from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favourite, Ingredient, IngredientRecipes, Recipe,
                            ShoppingCart, Subscription, Tag, TagRecipe)
from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscription.objects.filter(subscribing=obj, user=user).exists()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')

        extra_kwargs = {'password': {'write_only': True}}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSrializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return obj.recipe_is_favourite.filter(user=user).exists()
        # return Favourite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return obj.recipe_shopping_cart.filter(user=user).exists()
        # return ShoppingCart.objects.filter(recipe=obj, user=user).exists()

    def get_tags(self, instance):
        tags_recipes = []
        for tags in instance.tags.all():
            tags_recipes.append(model_to_dict(tags))

        return tags_recipes

    def get_author(self, instance):
        return model_to_dict(
            instance.author,
            fields=(
                'id',
                'username',
                'email',
                'first_name',
                'last_name',
                'is_subscribed')
        )

    def get_ingredients(self, instance):
        ingredients_recipes = []
        for ingredients in instance.ingredients.all():
            amount = model_to_dict(
                instance.ingredient_recipes.get(
                    ingredient=model_to_dict(ingredients)['id']
                )
            )['amount']
            ingredients_recipes.append(
                dict(
                    list(
                        model_to_dict(ingredients).items()
                    ) + list(
                        {'amount': amount}.items()
                    )
                )
            )
        return ingredients_recipes

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def create(self, validated_data):
        if 'tags' not in self.initial_data:
            return Recipe.objects.create(
                author=self.context['request'].user, **validated_data)

        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')

        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data)

        for tag_id in tags:
            current_tag = get_object_or_404(
                Tag.objects,
                pk=tag_id
            )

            TagRecipe.objects.create(
                tag=current_tag, recipe=recipe)

        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            ingredient_amount = ingredient['amount']
            current_ingredient = get_object_or_404(
                Ingredient.objects,
                pk=ingredient_id
            )
            IngredientRecipes.objects.create(
                ingredient=current_ingredient,
                amount=ingredient_amount,
                recipe=recipe
            )

        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        if 'tags' in self.initial_data:
            tags = self.initial_data.pop('tags')
            lst = []
            for tag in tags:
                current_tag = get_object_or_404(
                    Tag.objects,
                    pk=tag
                )
                lst.append(current_tag)

            instance.tags.set(lst)

        if 'ingredients' in self.initial_data:
            recipe = Recipe.objects.get(id=instance.id)
            IngredientRecipes.objects.filter(recipe=recipe).delete()

            ingredients = self.initial_data.pop('ingredients')
            lst = []

            for ingredient in ingredients:

                ingredient_id = ingredient['id']
                ingredient_amount = ingredient['amount']

                current_ingredient = get_object_or_404(
                    Ingredient.objects,
                    pk=ingredient_id
                )

                IngredientRecipes.objects.create(
                    ingredient=current_ingredient,
                    amount=ingredient_amount,
                    recipe=recipe
                )

        instance.save()
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data, author_id):
        if author_id == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        return data

    class Meta:
        model = Subscription
        fields = ('user',)

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscribing')
            )
        ]


class SubscriptionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('email', 'recipes_count')

    def to_representation(self, instance):

        recipes = []
        for recipe in instance.subscribing.recipes.all():

            if model_to_dict(recipe)['image']:
                image = self.context.get('request').build_absolute_uri(
                    model_to_dict(recipe)['image'].url)
            else:
                image = None

            recipe_author = {
                'id': model_to_dict(recipe)['id'],
                'name': model_to_dict(recipe)['name'],
                'image': image,
                'cooking_time': model_to_dict(recipe)['cooking_time']
            }

            recipes.append(recipe_author)

        return {
            'email': instance.subscribing.email,
            'id': instance.subscribing.id,
            'username': instance.subscribing.username,
            'first_name': instance.subscribing.first_name,
            'last_name': instance.subscribing.last_name,
            'is_subscribed': True,
            'recipes': recipes,
            'recipes_count': Recipe.objects.filter(
                author=instance.subscribing
            ).count()
        }


class FavouriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Favourite
        fields = ('user',)

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favourite.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'image': self.context.get(
                'request'
            ).build_absolute_uri(instance.image.url),
            'cooking_time': instance.cooking_time
        }


class ShoppingCartSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = ShoppingCart
        fields = ('user',)

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'image': self.context.get(
                'request'
            ).build_absolute_uri(instance.image.url),
            'cooking_time': instance.cooking_time
        }
