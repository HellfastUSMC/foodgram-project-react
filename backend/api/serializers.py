from itertools import product
from unicodedata import name
from rest_framework import serializers
from django.contrib.auth import get_user_model

from food.models import Tag, Product, Recipe, Ingridient


user = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    full_name = serializers.SerializerMethodField('get_full_name')

    def get_full_name(self, obj):
        return obj.get_full_name()

    class Meta:
        model = user
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


# class UnitSerializer(serializers.ModelSerializer):
#     """Сериализатор единиц измерения."""

#     class Meta:
#         model = Unit
#         fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""

    class Meta:
        model = Product
        fields = '__all__'


class IngridientSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    product = ProductSerializer()
    class Meta:
        model = Ingridient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    tags = serializers.SlugRelatedField('name', many=True, read_only=True)
    author = serializers.SlugRelatedField('username', read_only=True)
    ingridients = IngridientSerializer(many=True)
    #author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
