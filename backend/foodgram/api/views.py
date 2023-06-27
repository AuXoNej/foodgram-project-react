from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import exceptions
from rest_framework.viewsets import ModelViewSet
from users.models import User

from .filters import RecipeFilter
from .mixins import RetrieveListViewSet
from .permissions import IsAuthorOrAuthenticatedCreateOrReadOnly
from .serializers import (FavouriteSerializer, IngredientSerializer,
                          RecipeSrializer, ShoppingCartSerializer,
                          SubscriptionListSerializer, SubscriptionSerializer,
                          TagSerializer)
from recipes.models import (Favourite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Subscription, Tag)


class RecipeViewSet(ModelViewSet):
    """Вью для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSrializer
    permission_classes = (IsAuthorOrAuthenticatedCreateOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if Favourite.objects.filter(
                    user=request.user,
                    recipe=recipe).exists():
                raise exceptions.ValidationError('Рецепт уже в избранном')

            serializer = FavouriteSerializer(
                recipe,
                context={'request': request}
            )
            Favourite.objects.filter(recipe=recipe).create(
                user=request.user, recipe=recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Favourite.objects.filter(
                    user=request.user,
                    recipe=recipe).exists():
                raise exceptions.ValidationError('Рецепт не в избранном')

            Favourite.objects.filter(user=request.user, recipe=recipe).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError('Рецепт уже в списке покупок')

            serializer = ShoppingCartSerializer(
                recipe, context={'request': request})
            ShoppingCart.objects.filter(recipe=recipe).create(
                user=request.user, recipe=recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                    user=user,
                    recipe=recipe).exists():
                raise exceptions.ValidationError('Рецепт не в списке покупок')

            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET', ])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_carts = ShoppingCart.objects.filter(user=user)

        ingredients_recipe = {}
        for shopping_cart in shopping_carts:
            recipe = shopping_cart.recipe

            for ingredient_amount in IngredientAmount.objects.filter(
                recipe=recipe
            ):
                amount = ingredient_amount.amount

                measurement_unit = model_to_dict(
                    Ingredient.objects.get(
                        id=ingredient_amount.ingredient.id
                    )
                )['measurement_unit']
                if (ingredient_amount.ingredient.name in
                        ingredients_recipe.keys()):

                    ingredients_recipe[
                        ingredient_amount.ingredient.name
                    ][1] += amount
                else:
                    ingredients_recipe[ingredient_amount.ingredient.name] = [
                        measurement_unit, amount]

        shopping_list = ''
        for ingredient in ingredients_recipe.keys():
            shopping_list += (f'{ingredient}'
                              f'({ingredients_recipe[ingredient][0]}) - '
                              f'{ingredients_recipe[ingredient][1]}\n')

        return HttpResponse(
            shopping_list,
            content_type='text/plain; charset=utf8'
        )


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


class SubscriptionViewSet(ModelViewSet):
    serializer_class = SubscriptionListSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (SearchFilter,)
    search_fields = ('=subscribing__username',)

    def get_queryset(self):
        return Subscription.objects.filter(
            user=self.request.user
        )
    
    def retrieve(self, request, pk=None):
        user = request.user
        subscribing = get_object_or_404(User, id=pk)

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
            if not Subscription.objects.filter(
                    subscribing=subscribing).exists():

                raise exceptions.ValidationError(
                    'Вы не подписаны на этого пользователя')

            Subscription.objects.filter(subscribing=subscribing).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
        


"""
@api_view(('POST', 'DELETE')) 
@permission_classes((IsAuthenticated,)) 
def subscribe(self, request, pk):
    user = request.user
    subscribing = get_object_or_404(User, id=pk)

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
        if not Subscription.objects.filter(
                subscribing=subscribing).exists():

            raise exceptions.ValidationError(
                'Вы не подписаны на этого пользователя')

        Subscription.objects.filter(subscribing=subscribing).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_400_BAD_REQUEST)
"""
