from django.contrib.admin import ModelAdmin, register

from .models import (
    Ingredient, Product, Recipe, ShoppingCart, Subscription, Tag,
)


@register(Tag)
class TagAdmin(ModelAdmin):
    pass


@register(Product)
class ProductAdmin(ModelAdmin):
    pass


@register(Ingredient)
class IngridientAdmin(ModelAdmin):
    pass


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    pass


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    pass


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    pass
