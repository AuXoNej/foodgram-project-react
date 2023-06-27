from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionViewSet,
                    TagViewSet)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(
        'users/subscriptions',
        SubscriptionViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path(
        'users/<int:pk>/subscribe/',
        SubscriptionViewSet.as_view(
            {
                'post': 'retrieve',
                'delete': 'retrieve'
            }
        ),
        name='subscribe'
    ),
    path('', include(router_v1.urls), name='api_v1'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
]
