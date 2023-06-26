from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag
from users.models import User


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(
        field_name='author__id',
        to_field_name='id',
        queryset=User.objects.all()
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='get_queryset_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_queryset_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart',)

    def get_queryset_favorited(self, queryset, name, value):
        return queryset.filter(recipe_is_favourite__user=self.request.user)

    def get_queryset_shopping_cart(self, queryset, name, value):
        return queryset.filter(recipe_shopping_cart__user=self.request.user)
