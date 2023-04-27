from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, exceptions
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from recipes.models import Tag, Recipe, Ingredient, Subscription, Favourite, ShoppingCart, IngredientRecipes
from users.models import User

from django.forms.models import model_to_dict

from django.http import HttpResponse

from .mixins import CreateListViewSet, CreateDestroyListViewSet

from django.contrib.auth.decorators import login_required 
from rest_framework.decorators import api_view, permission_classes


#from .filters import TitleFilter
from .mixins import CreateDestroyListViewSet, CreateRetrieveListViewSet , RetrieveListViewSet



from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrAuthenticatedCreateOrReadOnly,
)


from .serializers import (
    TagSerializer,
    UserSignUpSerializer,
    UserSerializer,
    RecipeSrializer,
    IngredientSerializer,
    SubscriptionSerializer,
    SubscriptionListSerializer,
    FavouriteSerializer,
    ShoppingCartSerializer
)

from .utils import check_password
        

class UserViewSet(CreateRetrieveListViewSet):
    """Вью для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes_by_action = {'create': (AllowAny,),
                                    'list': (IsAuthenticated,)}
    lookup_field = 'id'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSignUpSerializer
        return UserSerializer
    
    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError: 
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Метод для url: 'me/'."""

        serializer = self.get_serializer(
            instance=request.user,
            partial=True,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


@action(detail=False, methods=('POST',))
class TokenObtainView(APIView):
    """Вью для получения токена."""

    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not password:
            return Response(
                {'password': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not email:
            return Response(
                {'email': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, email=email)

        if not check_password(user, password):
            return Response(
                {'password': ['Неверный пароль.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'auth_token': str(RefreshToken.for_user(user).access_token)},
            status=status.HTTP_200_OK,
        )


@action(detail=False, methods=('POST',))
class SetPasswordView(APIView):
    """Вью для получения изменения пароля."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')

        if not new_password:
            return Response(
                {'new_password': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not current_password:
            return Response(
                {'current_password': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user

        if not user.password == current_password:
            return Response(
                {'current_password': ['Неверный пароль.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        new_data = {'password': new_password}
        
        serializer = UserSerializer(instance=request.user, data=new_data, partial=True) 

        serializer.is_valid()
        serializer.save()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class RecipeViewSet(ModelViewSet):
    """Вью для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSrializer
    permission_classes = (IsAuthorOrAuthenticatedCreateOrReadOnly,)
    #pagination_class = LimitOffsetPagination
    #filter_backends = (SearchFilter,)

    search_fields = ('name', )

    """
    def get_serializer_class(self):
        if self.action in ('create'):
            return RecipePostSrializer
        return RecipeSrializer
    """

class TagViewSet(RetrieveListViewSet):
    """Вью для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    #pagination_class = LimitOffsetPagination
    #filter_backends = (SearchFilter,)

    search_fields = ('name', )

class IngredientViewSet(RetrieveListViewSet):
    """Вью для работы с ингридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    #pagination_class = LimitOffsetPagination
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
    id = author_id
    subscribing = get_object_or_404(User, id=id) 

    if request.method == 'POST':
        if user == subscribing:
            raise exceptions.ValidationError('Нельзя подписаться на самого себя')

        if Subscription.objects.filter(subscribing=subscribing).exists():
            raise exceptions.ValidationError('Вы уже подписаны на этого пользователя')

        serializer = SubscriptionSerializer(subscribing, context={'request':request})
        Subscription.objects.filter(subscribing=subscribing).create(user=request.user, subscribing=subscribing)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if not Subscription.objects.filter(subscribing=subscribing).exists():
            raise exceptions.ValidationError('Вы не подписаны на этого пользователя')

        Subscription.objects.filter(subscribing=subscribing).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(('POST', 'DELETE'))
@permission_classes((IsAuthenticated,))
def favorite(request, recipe_id): 
    id = recipe_id
    recipe = get_object_or_404(Recipe, id=id) 

    if request.method == 'POST':
        if Favourite.objects.filter(recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт уже в избранном')

        serializer = FavouriteSerializer(recipe, context={'request':request})
        Favourite.objects.filter(recipe=recipe).create(user=request.user, recipe=recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if not Favourite.objects.filter(recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт не в избранном')

        Favourite.objects.filter(recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(('POST', 'DELETE'))
@permission_classes((IsAuthenticated,))
def shopping_cart(request, recipe_id):
    user = request.user
    id = recipe_id
    recipe = get_object_or_404(Recipe, id=id)

    if request.method == 'POST':
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт уже в списке покупок')

        serializer = ShoppingCartSerializer(recipe, context={'request':request})
        ShoppingCart.objects.filter(recipe=recipe).create(user=request.user, recipe=recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт не в списке покупок')

        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def download_shopping_cart(request):
    user = request.user
    shopping_carts = ShoppingCart.objects.filter(user=user)

    ingredients_recipe = {}
    for shopping_cart in shopping_carts:
        #shopping_cart.recipe.ingredients
        recipe = shopping_cart.recipe
        
        for ingredient in recipe.ingredients.all():
            amount = model_to_dict(
                recipe.ingredient_recipes.get(ingredient=model_to_dict(ingredient)['id']))['amount']
            measurement_unit = model_to_dict(
                Ingredient.objects.get(id=model_to_dict(ingredient)['id']))['measurement_unit']
            if model_to_dict(ingredient)['name'] in ingredients_recipe.keys():
                ingredients_recipe[model_to_dict(ingredient)['name']][1] += amount#.append(model_to_dict(ingredient))
            else:
                ingredients_recipe[model_to_dict(ingredient)['name']] = [measurement_unit, amount]
        #ingredients_shopping_carts.append(model_to_dict(ingredients_recipe))
    
    shopping_list = ''
    for ingredient in ingredients_recipe.keys():
        shopping_list += f'{ingredient}({ingredients_recipe[ingredient][0]}) - {ingredients_recipe[ingredient][1]}\n'
    return HttpResponse(shopping_list, content_type='text/plain; charset=utf8')
