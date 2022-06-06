from django.contrib.admin import ModelAdmin, register
from .models import Subscribition, ShoppingCart


@register(Subscribition)
class SubscribitionAdmin(ModelAdmin):
    pass


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    pass
