from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.forms.models import model_to_dict

from rest_framework.response import Response
from rest_framework import status


from users.models import User
from recipes.models import Tag, Recipe, Ingredient, TagRecipe, IngredientRecipes, Subscription, Favourite, ShoppingCart

from .utils import get_confirmation_code, send_confirmation_email

import base64

from django.core.files.base import ContentFile


class UserSignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""

    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=150, required=True)


    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Зарезервированный username. Используйте другой.'
            )

        return username

    def validate(self, data):
        email = data['email']
        username = data['username']
        first_name = data['first_name']
        last_name = data['last_name']
        password = data['password']

        user = User.objects.filter(Q(username=username) | Q(email=email))

        if user and (user.get().password != password
                     or user.get().username != username):
            raise serializers.ValidationError(
                'Имя пользователя или password не соответствуют.'
            )

        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        email = validated_data.get('email')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        password = validated_data.get('password')

        send_confirmation_email(email, get_confirmation_code(user))
        return user
    
    
    def to_representation(self, instance):
        return {
            'email': instance.email,
            'id': instance.id,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name
        }


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscription.objects.filter(subscribing=obj, user=user).exists()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password', 'is_subscribed')
        
        extra_kwargs = {'password': {'write_only': True}}
 


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug') 


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')    


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
        return Favourite.objects.filter(recipe=obj, user=user).exists()
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(recipe=obj, user=user).exists()
    
    def get_tags(self, instance):
        tags_recipes = []
        for tags in instance.tags.all():
            tags_recipes.append(model_to_dict(tags))

        return tags_recipes
    
    def get_author(self, instance):
        return model_to_dict(instance.author, fields=('id', 'username', 'email', 'first_name', 'last_name', 'is_subscribed'))
    
    def get_ingredients(self, instance):
        ingredients_recipes = []
        for ingredients in instance.ingredients.all():
            amount = model_to_dict(
                instance.ingredient_recipes.get(ingredient=model_to_dict(ingredients)['id']))['amount']
            ingredients_recipes.append(dict(list(model_to_dict(ingredients).items()) + list({'amount': amount}.items())))
        return ingredients_recipes

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'image', 'name', 'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')

    def create(self, validated_data):        
        if 'tags' not in self.initial_data:
            recipe = Recipe.objects.create(author=self.context['request'].user, **validated_data)
            return recipe 
        
        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')

        recipe = Recipe.objects.create(author=self.context['request'].user, **validated_data)

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
                ingredient=current_ingredient, amount=ingredient_amount, recipe=recipe)


        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

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
            recipe = Recipe.objects.get(id=instance.id)#author=self.context['request'].user)
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
                        ingredient=current_ingredient, amount=ingredient_amount, recipe=recipe
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
                image = self.context.get('request').build_absolute_uri(model_to_dict(recipe)['image'].url)
            else:
                image = None

            recipe_author = {'id': model_to_dict(recipe)['id'],
                             'name': model_to_dict(recipe)['name'],
                             'image': image, 
                             'cooking_time': model_to_dict(recipe)['cooking_time'] 

            }
            recipes.append(recipe_author)

        user = self.context.get('request').user
        return {
            'email': instance.subscribing.email,
            'id' : instance.subscribing.id,
            'username' : instance.subscribing.username,
            'first_name' : instance.subscribing.first_name,
            'last_name' : instance.subscribing.last_name,
            'is_subscribed' : True,
            'recipes' : recipes,
            'recipes_count' : Recipe.objects.filter(author=instance.subscribing).count()
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
            'id' : instance.id,
            'name' : instance.name,
            'image' : self.context.get('request').build_absolute_uri(instance.image.url),
            'cooking_time' : instance.cooking_time
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
            'image': self.context.get('request').build_absolute_uri(instance.image.url),
            'cooking_time': instance.cooking_time
        }
