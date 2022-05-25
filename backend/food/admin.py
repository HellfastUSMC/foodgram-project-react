from django.contrib.admin import ModelAdmin, register
from .models import Tag


@register(Tag)
class TagAdmin(ModelAdmin):
    pass