from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet,
    TokenObtainView,
    UserViewSet,
    SetPasswordView,
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionViewSet,
    download_shopping_cart,
    subscribe,
    favorite,
    shopping_cart
)


app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users/subscriptions', SubscriptionViewSet, basename='subscriptions')
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('users/<int:author_id>/subscribe/', subscribe, name='subscribe'),
    path('users/set_password/', SetPasswordView.as_view(), name='set_password'),
    path('recipes/download_shopping_cart/', download_shopping_cart, name='download_shopping_cart'),
    path('recipes/<int:recipe_id>/favorite/', favorite, name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/', shopping_cart, name='shopping_cart'),
    path('', include(router_v1.urls), name='api_v1'),
    path('auth/token/login/', TokenObtainView.as_view(), name='token_obtain'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.urls.authtoken')),
]