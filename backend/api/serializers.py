from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField 

from food.models import Tag, Product, Recipe, Ingridient, Subscribition, ShoppingCart


user = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    #full_name = serializers.SerializerMethodField('get_full_name')
    is_subscribed = serializers.SerializerMethodField('check_subscribition')

    def get_full_name(self, obj):
        return obj.get_full_name()

    def check_subscribition(self, obj):
        request = self.context['request']
        print(obj.subscribers)
        if Subscribition.objects.filter(author=obj).filter(subscriber=request.user).exists():
            return 'true'
        else:
            return 'false'

    class Meta:
        model = user
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed'
        ]

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
    def to_internal_value(self, data):
        obj = get_object_or_404(Product, pk=data['id'])
        return obj
    class Meta:
        model = Product
        fields = '__all__'


class IngridientSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    class Meta:
        model = Ingridient
        fields = '__all__'


class IngridientViewSerializer(serializers.ModelSerializer):
    #product = ProductSerializer()
    name = serializers.CharField(source='product.name')
    class Meta:
        model = Ingridient
        fields = '__all__'



class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    #tags = TagSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingridients = serializers.PrimaryKeyRelatedField(queryset=Ingridient.objects.all(), many=True)
    author = serializers.SlugRelatedField('username', read_only=True)
    image = Base64ImageField()
    #ingridients = IngridientSerializer(many=True)
    #author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeViewSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingridients = IngridientViewSerializer(many=True)
    is_favorited = serializers.SerializerMethodField('_get_favorited', read_only=True)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def _get_favorited(self, obj):
        request = self.context.get('request', None)
        if obj.favorites.filter(pk=request.user.id).exists():
            return 1
        else:
            return 0

    class Meta:
        model = Recipe
        fields = '__all__'


class UserSupscriptionsSerializer(serializers.ModelSerializer): # STOPS HERE!!!
    recipes = RecipeViewSerializer(many=True, fields=['id', 'name', 'image', 'cooking_time'])
    recipes_count = len(recipes.data)

    class Meta:
        model = Subscribition
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes'
        ]
