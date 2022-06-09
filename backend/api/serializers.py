from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField 

from food.models import Tag, Product, Recipe, Ingridient, Subscription, ShoppingCart


user = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""
    is_subscribed = serializers.SerializerMethodField('check_subscription')

    def check_subscription(self, obj):
        request = self.context['request']
        if request.user.is_authenticated:
            if Subscription.objects.filter(author=obj).filter(
                subscriber=request.user
            ).exists():
                return 'true'
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


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    class Meta:
        model = Product
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngridientSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    name = serializers.CharField(source='product.name')
    measurement_unit = serializers.CharField(source='product.measurement_unit')

    class Meta:
        model = Ingridient
        exclude = ['product']


class IngridientViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = '__all__'

class IngridientField(serializers.Field):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value

class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)
    #ingridients = IngridientSerializer(many=True)
    ingridients = IngridientField()
    is_favorited = serializers.SerializerMethodField('_get_favorited', read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField('_get_shopping_cart', read_only=True)
    image = Base64ImageField()

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags.all(), many=True).data
        return representation

    def _get_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if obj.shopping_carts.filter(customer_id=request.user.id).exists():
            return 'true'
        else:
            return 'false'

    def _get_favorited(self, obj):
        request = self.context.get('request', None)
        if obj.favorites.filter(pk=request.user.id).exists():
            return 'true'
        else:
            return 'false'

    class Meta:
        model = Recipe
        exclude = ['favorites']


# class RecipeViewSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True)
#     author = UserSerializer()
#     ingridients = IngridientViewSerializer(many=True)
#     is_favorited = serializers.SerializerMethodField('_get_favorited', read_only=True)
#     is_in_shopping_cart = serializers.SerializerMethodField('_get_shopping_cart', read_only=True)

#     def __init__(self, *args, **kwargs):
#         # Don't pass the 'fields' arg up to the superclass
#         fields = kwargs.pop('fields', None)

#         # Instantiate the superclass normally
#         super().__init__(*args, **kwargs)

#         if fields is not None:
#             # Drop any fields that are not specified in the `fields` argument.
#             allowed = set(fields)
#             existing = set(self.fields)
#             for field_name in existing - allowed:
#                 self.fields.pop(field_name)

#     def _get_shopping_cart(self, obj):
#         request = self.context.get('request', None)
#         if obj.shopping_carts.filter(customer_id=request.user.id).exists():
#             return 'true'
#         else:
#             return 'false'

#     def _get_favorited(self, obj):
#         request = self.context.get('request', None)
#         if obj.favorites.filter(pk=request.user.id).exists():
#             return 'true'
#         else:
#             return 'false'

#     class Meta:
#         model = Recipe
#         #fields = '__all__'
#         exclude = ['favorites']


class UserSupscriptionsSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField('get_limited_recipes')
    recipes_count = serializers.SerializerMethodField('count_recipes')
    is_subscribed = serializers.SerializerMethodField('check_subscription')

    class Meta:
        model = user
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_limited_recipes(self, obj):
        print(self.context['request'].query_params.get('recipes_limit', None))
        limit = self.context['request'].query_params.get('recipes_limit', None)
        if limit is not None:
            queryset = obj.recipes.all().order_by('id')[:int(limit)]
        else:
            queryset = obj.recipes.all().order_by('id')
        data = RecipeSerializer(
            queryset,
            many=True,
            fields=['id', 'name', 'image', 'cooking_time']
        ).data
        return data

    def count_recipes(self, obj):
        return obj.recipes.count()

    def check_subscription(self, obj):
        request = self.context['request']
        if Subscription.objects.filter(author=obj).filter(
            subscriber=request.user
        ).exists():
            return 'true'
        return 'false'
