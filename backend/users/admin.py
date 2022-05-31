from django.contrib.admin import ModelAdmin, register
from .models import Subscribition


@register(Subscribition)
class SubscribitionAdmin(ModelAdmin):
    pass