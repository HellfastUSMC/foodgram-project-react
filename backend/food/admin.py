from django.contrib.admin import ModelAdmin, register
from .models import Ingridient, Product, Recipe, Tag, ShoppingCart, Subscription


@register(Tag)
class TagAdmin(ModelAdmin):
    pass


@register(Product)
class ProductAdmin(ModelAdmin):
    pass


@register(Ingridient)
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