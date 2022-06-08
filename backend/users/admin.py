from django.contrib.admin import ModelAdmin, register

from .models import CustomUser

@register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    pass