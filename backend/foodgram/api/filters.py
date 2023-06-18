from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='get_queryset_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_queryset_shopping_cart'
    )

    def get_queryset_favorited(self, queryset, name, value):
        return queryset.filter(favourite__user=self.request.user)

    def get_queryset_shopping_cart(self, queryset, name, value):
        return queryset.filter(shoppingcart__user=self.request.user)

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart',)
