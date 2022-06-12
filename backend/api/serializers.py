from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from food.models import (Ingredient, Product, Recipe, ShoppingCart,
                         Subscription, Tag)

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

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password')
        return representation

    class Meta:
        model = user
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
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


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    name = serializers.CharField(source='product.name')
    measurement_unit = serializers.CharField(source='product.measurement_unit')

    class Meta:
        model = Ingredient
        exclude = ['product']


class IngredientViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        '_get_post_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        '_get_favorited', read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        '_get_shopping_cart', read_only=True
    )
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
        if 'tags' in self.fields:
            representation['tags'] = TagSerializer(
                instance.tags.all(),
                many=True
            ).data
        return representation

    def _get_post_ingredients(self, obj):
        request = self.context.get('request', None)
        if request.method == 'GET':
            return IngredientSerializer(obj.ingredients.all(), many=True).data
        if request.method == 'POST':
            for ingredient in request.data['ingredients']:
                msg = {}
                if not Ingredient.objects.filter(pk=ingredient['id']).exists():
                    msg['ingredients'] = (
                        f'Объект не найден, проверьте'
                        f'значение поля id - {ingredient["id"]}'
                    )
                if 0 >= ingredient['amount'] or not isinstance(
                    ingredient['amount'],
                    int
                ):
                    msg['amount'] = (
                        f'Проверьте значение поля amount '
                        f'- {ingredient["amount"]}'
                    )
                if msg:
                    raise serializers.ValidationError(msg, code=400)
                instance = Ingredient.objects.create(
                    product=get_object_or_404(Product, pk=ingredient['id']),
                    amount=ingredient['amount']
                )
                obj.ingredients.add(instance)
            return IngredientSerializer(obj.ingredients.all(), many=True).data
        if request.method == 'PATCH':
            if request.data['ingredients']:
                for old_ingredient in obj.ingredients.all():
                    old_ingredient.delete()
                obj.ingredients.clear()
                for ingredient in request.data['ingredients']:
                    msg = {}
                    if not Ingredient.objects.filter(
                        pk=ingredient['id']
                    ).exists():
                        msg['ingredients'] = (
                            f'Объект не найден, проверьте'
                            f'значение поля id - {ingredient["id"]}'
                        )
                    if 0 >= ingredient['amount'] or not isinstance(
                        ingredient['amount'],
                        int
                    ):
                        msg['amount'] = (
                            f'Проверьте значение поля amount '
                            f'- {ingredient["amount"]}'
                        )
                    if msg:
                        raise serializers.ValidationError(msg, code=400)
                    instance = Ingredient.objects.create(
                        product=get_object_or_404(
                            Product,
                            pk=ingredient['id']
                        ),
                        amount=ingredient['amount']
                    )
                    obj.ingredients.add(instance)
                return IngredientSerializer(
                    obj.ingredients.all(),
                    many=True
                ).data

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
        limit = self.context['request'].query_params.get('recipes_limit', None)
        if limit is not None:
            queryset = obj.recipes.all().order_by('id')[:int(limit)]
        else:
            queryset = obj.recipes.all().order_by('id')
        data = RecipeSerializer(
            queryset,
            many=True,
            fields=['id', 'name', 'image', 'cooking_time', 'ingredients'],
            context={'request': self.context['request']}
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


class ShoppingCartSerializer(serializers.ListSerializer):
    ingredients = serializers.SerializerMethodField('_get_recipes_serializer')

    def _get_recipes_serializer(self):
        request = self.context['request']
        serializer = RecipeSerializer(read_only=True, many=True, context={'request': request})
        return serializer.data

    class Meta:
        model = Recipe
        fields = [
            'recipes',
        ]
