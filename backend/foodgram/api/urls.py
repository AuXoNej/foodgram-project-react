from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionViewSet,
                    TagViewSet)

app_name = 'api'

router_v1 = DefaultRouter()

"""
path('users/subscriptions/', SubscriptionViewSet.subscriptions),
path('users/<int:pk>/subscribe/', SubscriptionViewSet.subscribe.a),
path('', include('djoser.urls')),
"""

router_v1.register(
    'users/subscriptions',
    SubscriptionViewSet,
    basename='subscriptions'
)
router_v1.register(
    'users/<int:pk>/subscribe',
    SubscriptionViewSet.subscribe.as_view(),
    basename='subscribe'
)

router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router_v1.urls), name='api_v1'),
]
