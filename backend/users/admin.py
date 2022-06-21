from django.contrib.admin import ModelAdmin, register

from .models import CustomUser


@register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    search_fields = ('username__incontains', 'email__incontains')
    list_filter = ('username', 'email')
