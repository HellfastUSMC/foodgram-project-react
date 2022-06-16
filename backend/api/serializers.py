from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from food.models import (Ingredient, Product, Recipe,
                         Subscription, Tag, ShoppingCart)

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
                return True
        return False

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        ShoppingCart.objects.create(customer=instance)
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
    amount = serializers.IntegerField(source='ingridient.amount', read_only=True)

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
    id = serializers.ReadOnlyField(source='product.id') # New field 4 test
    name = serializers.ReadOnlyField(source='product.name')
    measurement_unit = serializers.ReadOnlyField(
        source='product.measurement_unit'
    )

    class Meta:
        model = Ingredient
        exclude = ['product', 'recipe']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор названий продуктов."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(source='ingredient_set', many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        '_get_favorited', read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        '_get_shopping_cart', read_only=True
    )
    image = Base64ImageField(represent_in_base64=False)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def _create_ingredients(self, obj, ingredients):
        saved_args = locals()
        print(saved_args)
        for ingredient in ingredients:
            Ingredient.objects.create(
                product_id=int(ingredient['id']),
                amount=int(ingredient['amount']),
                recipe_id=obj.id
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        tags_objs = Tag.objects.filter(id__in=tags)
        #obj = Recipe.objects.create(**validated_data)
        obj = Recipe.objects.create(name='123', text='123', cooking_time=99, author=get_object_or_404(user, pk=1))
        self._create_ingredients(obj, ingredients)
        obj.tags.set(tags_objs)
        return obj

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        tags_objs = Tag.objects.filter(id__in=tags)
        obj = Recipe(**validated_data)
        obj.save()
        self._create_ingredients(obj, ingredients)
        obj.tags.set(tags_objs)
        return obj

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'tags' in self.fields:
            representation['tags'] = TagSerializer(
                instance.tags.all(),
                many=True
            ).data
        if 'ingredients' in self.fields:
            representation['ingredients'] = IngredientSerializer(
                Ingredient.objects.filter(recipe=instance),
                many=True
            ).data
        return representation

    def to_internal_value(self, data):
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
