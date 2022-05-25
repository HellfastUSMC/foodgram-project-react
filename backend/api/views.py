from django.shortcuts import render
from rest_framework import permissions, viewsets
from django.contrib.auth import get_user_model

from . import serializers, pagination

from food.models import Tag

user = get_user_model()


class BaseViewSet(viewsets.ModelViewSet):
    """Базовая вьюха."""
    #permission_classes = [IsAdmin | ReadOnly]
    permission_classes = [permissions.AllowAny]
    pagination_class = pagination.DefaultPagination


class UserViewset(BaseViewSet):
    queryset = user.objects.all()
    serializer_class = serializers.UserSerializer


class TagViewset(BaseViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer