from rest_framework import permissions, viewsets, generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from . import serializers, pagination

from food.models import Tag, Product, Recipe, Ingridient

user = get_user_model()


class BaseViewSet(viewsets.ModelViewSet):
    """Базовая вьюха."""
    #permission_classes = [IsAdmin | ReadOnly]
    permission_classes = [permissions.AllowAny]
    pagination_class = pagination.DefaultPagination


class UserViewset(BaseViewSet):
    """Вьюха пользователей"""
    queryset = user.objects.all()
    serializer_class = serializers.UserSerializer


class TagViewset(BaseViewSet):
    """Вьюха тэгов"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ProductViewset(BaseViewSet):
    """Вьюха продуктов"""
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer


# class UnitViewset(BaseViewSet):
#     """Вьюха единиц измерения"""
#     queryset = Unit.objects.all()
#     serializer_class = serializers.UnitSerializer


class RecipeViewset(BaseViewSet):
    """Вьюха рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer


class IngridientViewset(BaseViewSet):
    """Вьюха ингридиентов"""
    queryset = Ingridient.objects.all()
    serializer_class = serializers.IngridientSerializer


class UserMeViewset(viewsets.ViewSet):
    def retrieve(self, request):
        queryset = user.objects.all()
        me = get_object_or_404(queryset, pk=request.user.id)
        serializer = serializers.UserSerializer(me)
        return Response(serializer.data)
