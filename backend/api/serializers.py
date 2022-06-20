import os

from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.core import exceptions
from django.forms import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from . import utils
from food.models import (
    Ingredient, Product, Recipe, Subscription, Tag,
)

user = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""
    is_subscribed = serializers.SerializerMethodField('check_subscription')
    password = serializers.CharField(
        required=True,
        write_only=True
    )

    def check_subscription(self, obj):
        request = self.context['request']
        if request.user.is_authenticated:
            return Subscription.objects.filter(author=obj).filter(
                subscriber=request.user
            ).exists()

    def validate_password(self, data):
        cur_user = user(**self.initial_data)
        errors = []

        try:
            password_validation.validate_password(password=data, user=cur_user)
        except exceptions.ValidationError as val_err:
            errors.append(list(val_err.messages))

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        cur_user = user.objects.create_user(**validated_data)
        cur_user.save()
        return cur_user

    class Meta:
        model = user
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'is_subscribed',
        ]


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор типов продуктов."""
    amount = serializers.IntegerField(
        source='ingridient.amount',
        read_only=True
    )

    class Meta:
        model = Product
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    id = serializers.ReadOnlyField(source='product.id')
    name = serializers.ReadOnlyField(source='product.name')
    measurement_unit = serializers.ReadOnlyField(
        source='product.measurement_unit'
    )

    class Meta:
        model = Ingredient
        exclude = ['product', 'recipe']


class IngField(serializers.Field):

    def to_internal_value(self, data):
        for ingredient in data:
            msg = {}
            if not Product.objects.filter(pk=ingredient['id']).exists():
                msg['id'] = (f'Продукт с id {ingredient["id"]}'
                             f' отсутствует в базе.')
            if (not isinstance(int(ingredient['amount']), int)
                    or int(ingredient['amount']) <= 0):
                msg['amount'] = 'Количество должно быть числом больше 0.'
            if msg:
                raise ValidationError(msg)
        return data

    def to_representation(self, data):
        ingredients_data = IngredientSerializer(
            Ingredient.objects.filter(recipe=data.instance), many=True
        ).data
        return ingredients_data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngField()
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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        obj = super().create(validated_data)
        obj.tags.set(tags)
        utils.create_ingredients(obj, ingredients)
        return obj

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            new_ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        utils.create_ingredients(instance, new_ingredients)
        if 'image' in validated_data:
            old_image_path = instance.image
            os.remove(os.path.join(settings.MEDIA_ROOT, str(old_image_path)))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'tags' in self.fields:
            representation['tags'] = TagSerializer(
                instance.tags.all(),
                many=True
            ).data
        return representation

    def validate_image(self, data):
        if not data:
            raise ValidationError('Это поле не может быть пустым.')
        return data

    def validate(self, attrs):
        if 'ingredients' not in self.initial_data:
            raise ValidationError({'ingredients': 'Обязательное поле.'})
        if not self.initial_data['ingredients']:
            raise ValidationError(
                {'ingredients': 'Это поле не может быть пустым.'}
            )
        return super().validate(attrs)

    def _get_shopping_cart(self, obj):
        request = self.context.get('request')
        return obj.shopping_carts.filter(customer_id=request.user.id).exists()

    def _get_favorited(self, obj):
        request = self.context.get('request')
        return obj.favorites.filter(pk=request.user.id).exists()

    class Meta:
        model = Recipe
        exclude = ['favorites', 'published']


class UserSupscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
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
            queryset = obj.recipes.all().order_by('-published')[:int(limit)]
        else:
            queryset = obj.recipes.all().order_by('-published')
        data = RecipeSerializer(
            queryset,
            many=True,
            fields=['id', 'name', 'image', 'cooking_time'],
            context={'request': self.context['request']}
        ).data
        return data

    def count_recipes(self, obj):
        return obj.recipes.count()

    def check_subscription(self, obj):
        request = self.context['request']
        return Subscription.objects.filter(author=obj).filter(
            subscriber=request.user
        ).exists()
