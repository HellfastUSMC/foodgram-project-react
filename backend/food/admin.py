from django.contrib.admin import ModelAdmin, register
from django.db.models import Count

from .models import (Ingredient, Product, Recipe, ShoppingCart, Subscription,
                     Tag)


@register(Tag)
class TagAdmin(ModelAdmin):
    pass


@register(Product)
class ProductAdmin(ModelAdmin):
    pass


@register(Ingredient)
class IngridientAdmin(ModelAdmin):
    list_filter = ('product__name',)
    search_fields = ('product__name__icontains',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    readonly_fields = ['fav_count', ]
    list_display = (
        'name', 'author_name', 'cooking_time',
        'fav_count', 'show_tags', 'show_ingredients'
    )
    list_filter = ('name', 'tags', 'author__username', )
    search_fields = (
        'name__icontains', 'tags__name__icontains',
        'author__username__icontains'
    )

    def author_name(self, obj):
        return obj.author.username
    author_name.short_description = 'Автор'

    def show_ingredients(self, obj):
        return '\n'.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )
    show_ingredients.short_description = 'Ингредиенты'

    def show_tags(self, obj):
        return '\n'.join([tag.name for tag in obj.tags.all()])
    show_tags.short_description = 'Тэги'

    def fav_count(self, obj):
        return obj.fav_count
    fav_count.short_description = 'Счетчик избранного'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(fav_count=Count('favorites'))
        return queryset


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    pass


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    pass
