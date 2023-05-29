from django.contrib import admin

from .models import (Favourite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Subscription, Tag)

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Subscription)
admin.site.register(Favourite)
admin.site.register(ShoppingCart)
admin.site.register(IngredientAmount)


class RecipeTags(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


@admin.register(Recipe)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_display_links = ('name',)
    list_filter = ('name', 'author__username', 'tags')
    search_fields = ('name',)
    inlines = (RecipeTags,)
