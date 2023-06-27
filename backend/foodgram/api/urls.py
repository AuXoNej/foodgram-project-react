from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionViewSet,
                    TagViewSet)

app_name = 'api'

router_v1 = DefaultRouter()

"""
path('users/subscriptions/', SubscriptionViewSet.subscriptions),
path('users/<int:pk>/subscribe/', SubscriptionViewSet.subscribe),
"""

router_v1.register(
    'users',
    SubscriptionViewSet,
    basename='subscriptions'
)

router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router_v1.urls), name='api_v1'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
]
