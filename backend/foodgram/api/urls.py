from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionViewSet,
                    TagViewSet, download_shopping_cart, favorite,
                    shopping_cart, subscribe)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(
    'users/subscriptions',
    SubscriptionViewSet,
    basename='subscriptions'
)
router_v1.register('recipe', RecipeViewSet, basename='recipe')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('users/<int:author_id>/subscribe/', subscribe, name='subscribe'),
    path('recipes/download_shopping_cart/',
         download_shopping_cart, name='download_shopping_cart'),
    path('recipes/<int:recipe_id>/favorite/', favorite, name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         shopping_cart, name='shopping_cart'),
    path('', include(router_v1.urls), name='api_v1'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),

]
