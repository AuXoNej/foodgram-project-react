from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (Favourite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Subscription, Tag)
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import exceptions
from rest_framework.viewsets import ModelViewSet
from users.models import User

from .mixins import RetrieveListViewSet
from .permissions import IsAuthorOrAuthenticatedCreateOrReadOnly
from .serializers import (FavouriteSerializer, IngredientSerializer,
                          RecipeSrializer, ShoppingCartSerializer,
                          SubscriptionListSerializer, SubscriptionSerializer,
                          TagSerializer)


class RecipeViewSet(ModelViewSet):
    """Вью для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSrializer
    """
    permission_classes = (IsAuthorOrAuthenticatedCreateOrReadOnly,)
    
    from django_filters.rest_framework import DjangoFilterBackend
    pagination_class = None
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_fields = ('tags', )
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_fields = ('tags')
    search_fields = ('tags', )
    """


class TagViewSet(RetrieveListViewSet):
    """Вью для работы с тегами."""

    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None
    serializer_class = TagSerializer


class IngredientViewSet(RetrieveListViewSet):
    """Вью для работы с ингридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None
    filter_backends = (SearchFilter,)

    search_fields = ('name', )


@action(detail=False, methods=('GET',))
class SubscriptionViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionListSerializer
    permission_classes = (IsAuthenticated, )

    filter_backends = (filters.SearchFilter, )
    search_fields = ('=subscribing__username',)


@api_view(('POST', 'DELETE'))
@permission_classes((IsAuthenticated,))
def subscribe(request, author_id):
    user = request.user
    subscribing = get_object_or_404(User, id=author_id)

    if request.method == 'POST':
        if user == subscribing:
            raise exceptions.ValidationError(
                'Нельзя подписаться на самого себя')

        if Subscription.objects.filter(subscribing=subscribing).exists():
            raise exceptions.ValidationError(
                'Вы уже подписаны на этого пользователя')

        serializer = SubscriptionSerializer(
            subscribing, context={'request': request})
        Subscription.objects.filter(subscribing=subscribing).create(
            user=request.user, subscribing=subscribing)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if not Subscription.objects.filter(subscribing=subscribing).exists():
            raise exceptions.ValidationError(
                'Вы не подписаны на этого пользователя')

        Subscription.objects.filter(subscribing=subscribing).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST', 'DELETE'))
@permission_classes((IsAuthenticated,))
def favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        if Favourite.objects.filter(recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт уже в избранном')

        serializer = FavouriteSerializer(recipe, context={'request': request})
        Favourite.objects.filter(recipe=recipe).create(
            user=request.user, recipe=recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if not Favourite.objects.filter(recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт не в избранном')

        Favourite.objects.filter(recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST', 'DELETE'))
@permission_classes((IsAuthenticated,))
def shopping_cart(request, recipe_id):
    user = request.user
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт уже в списке покупок')

        serializer = ShoppingCartSerializer(
            recipe, context={'request': request})
        ShoppingCart.objects.filter(recipe=recipe).create(
            user=request.user, recipe=recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт не в списке покупок')

        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def download_shopping_cart(request):
    user = request.user
    shopping_carts = ShoppingCart.objects.filter(user=user)

    ingredients_recipe = {}
    for shopping_cart in shopping_carts:
        recipe = shopping_cart.recipe

        for ingredient in IngredientAmount.objects.filter(recipe=recipe):
            amount = ingredient['amount']
            measurement_unit = model_to_dict(
                Ingredient.objects.get(
                    id=model_to_dict(ingredient)['id']
                )
            )['measurement_unit']
            if model_to_dict(ingredient)['name'] in ingredients_recipe.keys():
                ingredients_recipe[model_to_dict(
                    ingredient)['name']][1] += amount
            else:
                ingredients_recipe[model_to_dict(ingredient)['name']] = [
                    measurement_unit, amount]

    shopping_list = ''
    for ingredient in ingredients_recipe.keys():
        shopping_list += (f'{ingredient}'
                          f'({ingredients_recipe[ingredient][0]}) - '
                          f'{ingredients_recipe[ingredient][1]}\n')

    return HttpResponse(shopping_list, content_type='text/plain; charset=utf8')
