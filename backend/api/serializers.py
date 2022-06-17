from tkinter import Image
from django.core import exceptions
from django.contrib.auth import get_user_model, password_validation
import base64
import io
from PIL import Image as pil_image
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from food.models import (Ingredient, Product, Recipe,
                         Subscription, Tag, ShoppingCart)

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
            if Subscription.objects.filter(author=obj).filter(
                subscriber=request.user
            ).exists():
                return True
        return False

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
        ShoppingCart.objects.create(customer=cur_user)
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
    id = serializers.ReadOnlyField(source='product.id') # New field 4 test
    name = serializers.ReadOnlyField(source='product.name')
    measurement_unit = serializers.ReadOnlyField(
        source='product.measurement_unit'
    )

    class Meta:
        model = Ingredient
        exclude = ['product', 'recipe']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(
        source='ingredient_set',
        many=True,
        #read_only=True
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

    def create(self, validated_data):
        #print(validated_data)
        ingredients = validated_data.pop('ingredient_set')
        tags = validated_data.pop('tags')
        #image = validated_data.pop('image')
        #validated_data['image'] = self._decode_image(image)
        tags_objs = Tag.objects.filter(id__in=tags)
        #obj = Recipe.objects.create(**validated_data, image=image)
        obj = super().create(validated_data)
        self._create_ingredients(obj, ingredients)
        obj.tags.set(tags_objs)
        return obj

    # def update(self, instance, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     image = validated_data.pop('image')
    #     #author = validated_data.pop('author')
    #     #instance.image = validated_data.pop('image')
    #     tags_objs = Tag.objects.filter(id__in=tags)
    #     #print(ingredients)
    #     #Recipe.objects.filter(pk=instance.id).update(**validated_data)
    #     #print(instance.ingredients.filter(ingredient__recipe=instance).values())
    #     obj = Recipe(**validated_data)
    #     #obj.save(pushlished=instance.published, image=image)
    #     #obj = self.update(self.instance, validated_data)
    #     self._create_ingredients(instance, ingredients)
    #     instance.tags.set(tags_objs)
    #     return super().update(instance, validated_data)

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     if 'tags' in self.fields:
    #         representation['tags'] = TagSerializer(
    #             instance.tags.all(),
    #             many=True
    #         ).data
    #     if 'ingredients' in self.fields:
    #         representation['ingredients'] = IngredientSerializer(
    #             Ingredient.objects.filter(recipe=instance),
    #             many=True
    #         ).data
    #     return representation

    def to_internal_value(self, data):
        print(data)
        #data['tags'] = Tag.objects.filter(id__in=data['tags'])
        return super().to_internal_value(data)

    # def validate_nested_tags(self, data):
    #     msg = []
    #     if 'tags' not in self.initial_data:
    #         msg.append('Обязательное поле.')
    #     if not self.initial_data['tags']:
    #         msg.append('Это поле не может быть пустым.')
    #     raise ValidationError(msg)

    def validate_image(self, data):
        msg = ''
        if not data:
            msg = 'Это поле не может быть пустым.'
        if 'image' not in self.initial_data:
            msg = 'Обязательное поле.'
        if msg:
            raise ValidationError(msg)
        return data


    def _get_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if obj.shopping_carts.filter(customer_id=request.user.id).exists():
            return True
        return False

    def _get_favorited(self, obj):
        request = self.context.get('request', None)
        if obj.favorites.filter(pk=request.user.id).exists():
            return True
        return False

    class Meta:
        model = Recipe
        exclude = ['favorites', 'published']


    # def _get_post_ingredients(self, obj):
    #     request = self.context.get('request', None)

    #     def validate_request(ingredient_id, ingredient_amount):
    #         msg = {}
    #         if not Product.objects.filter(pk=int(ingredient_id)).exists():
    #             msg['ingredients'] = (
    #                 f'Объект не найден, проверьте'
    #                 f'значение поля id - {ingredient_id}'
    #             )
    #         if 0 >= int(ingredient_amount):
    #             msg['amount'] = (
    #                 f'Проверьте значение поля amount '
    #                 f'- {ingredient_amount}'
    #             )
    #         return msg

    #     if (
    #         request.method == 'GET'
    #         or 'shopping_cart' in request.get_full_path()
    #         or 'view' not in self.context
    #     ):
    #         return IngredientSerializer(obj.ingredients.all(), many=True).data

        # if request.method == 'POST':
        #     if 'ingredients' not in request.data:
        #         raise serializers.ValidationError(
        #             {'ingredients': 'Поле ingredients обязательное'},
        #             code=400
        #         )
        #     for ingredient in request.data['ingredients']:
        #         msg = validate_request(ingredient['id'], ingredient['amount'])
        #         if msg:
        #             raise serializers.ValidationError(msg, code=400)
        #         instance = Ingredient.objects.create(
        #             product=get_object_or_404(Product, pk=ingredient['id']),
        #             amount=ingredient['amount']
        #         )
        #         obj.ingredients.add(instance)
        #     return IngredientSerializer(obj.ingredients.all(), many=True).data

        # if request.method == 'PATCH' and 'ingredients' in request.data:
        #     #obj.ingredients.clear()
        #     for ingredient in request.data['ingredients']:
        #         msg = validate_request(ingredient['id'], ingredient['amount'])
        #         if msg:
        #             raise serializers.ValidationError(msg, code=400)
        #         instance, exists = Ingredient.objects.get_or_create(
        #             product__id=int(ingredient['id']),
        #             amount=int(ingredient['amount'])
        #         )
        #         obj.ingredients.add(instance)
        #     return IngredientSerializer(
        #         obj.ingredients.all(),
        #         many=True
        #     ).data
        # extra_kwargs = {
        #     'ingredients': {'required': True, 'allow_blank': False}
        # }


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
        if Subscription.objects.filter(author=obj).filter(
            subscriber=request.user
        ).exists():
            return True
        return False
