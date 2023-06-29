from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import (Favourite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Subscription, Tag)

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Subscription)
admin.site.register(Favourite)
admin.site.register(ShoppingCart)


class RequiredInlineFormSet(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        if i < 1:
            form.empty_permitted = False
        return form


class RecipeTags(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


class RecipeIngredient(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    formset = RequiredInlineFormSet


@admin.register(Recipe)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_display_links = ('name',)
    list_filter = ('name', 'author__username', 'tags')
    search_fields = ('name',)
    inlines = (RecipeTags, RecipeIngredient)

    readonly_fields = ('in_favorites',)

    def in_favorites(self, obj):
        return Favourite.objects.filter(recipe=obj).count()
    in_favorites.short_description = 'В избранном у пользователей'
