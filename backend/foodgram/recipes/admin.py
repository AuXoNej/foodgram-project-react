from django.contrib import admin

from .models import (Favourite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Subscription, Tag)

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Subscription)
admin.site.register(Favourite)
admin.site.register(ShoppingCart)


class RecipeTags(admin.TabularInline):
    model = Recipe.tags.through
    blank=True
    extra = 1


class RecipeIngredient(admin.TabularInline):
    model = IngredientAmount
    blank=True


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
