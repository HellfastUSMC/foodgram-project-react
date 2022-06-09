from rest_framework import (
    permissions,
    viewsets,
    views,
    status,
    filters,
    mixins
)  # ПОИСК ПО СТРОКЕ
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from . import serializers, pagination, permissions as local_rights

from food.models import Tag, Product, Recipe, Subscription, ShoppingCart

user = get_user_model()


class TokenLogout(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ref_str = RefreshToken.for_user(request.user)
        token = RefreshToken(ref_str)
        token.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseViewSet(viewsets.ModelViewSet):
    """Базовая вьюха."""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = pagination.DefaultPagination


class UserViewset(BaseViewSet):
    """Вьюха пользователей"""
    permission_classes = [local_rights.IsOwnerOrReadOnlyAndPostAll]
    queryset = user.objects.all().order_by('id')
    serializer_class = serializers.UserSerializer

    def get_object(self):
        if 'me' in self.request.get_full_path():
            obj = self.request.user
        else:
            obj = get_object_or_404(user, pk=self.kwargs['pk'])
        print(obj)
        return obj


class TagViewset(BaseViewSet):
    """Вьюха тэгов"""
    queryset = Tag.objects.all().order_by('id')
    serializer_class = serializers.TagSerializer

    def update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод запрещен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод запрещен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод запрещен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод запрещен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class ProductViewset(BaseViewSet):
    """Вьюха продуктов"""
    queryset = Product.objects.all().order_by('id')
    serializer_class = serializers.ProductSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    def update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод запрещен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод запрещен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод запрещен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод запрещен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class RecipeViewset(BaseViewSet):
    """Вьюха рецептов"""
    serializer_class = serializers.RecipeSerializer
    permission_classes = [local_rights.IsAuthenticatedAndOwner, ]
    
    def create(self, request, *args, **kwargs):
        #print(request.data)
        super().create(request, *args, **kwargs)
        return Response(
            serializers.RecipeSerializer(
                self.request.user.recipes.last(),
                context={'request': self.request}).data
            )

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        for ingridient in instance.ingridients.all():
            ingridient.delete()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('id')
        if self.request.GET.get('is_favorited') == '1':
            queryset = queryset.filter(favorites__id=self.request.user.id)
        if self.request.GET.getlist('tags'):
            queryset = queryset.filter(
                tags__slug__in=self.request.GET.getlist('tags')
            )
        if self.request.GET.get('author'):
            queryset = queryset.filter(
                author__id=self.request.GET.get('author')
            )
        return queryset.order_by('id')

    # def get_serializer_class(self):
    #     if self.action in ['list', 'retrieve']:
    #         return serializers.RecipeViewSerializer
    #     else:
    #         return serializers.RecipeSerializer


# class IngridientViewset(BaseViewSet):
#     """Вьюха ингридиентов"""
#     queryset = Ingridient.objects.all().order_by('id')
#     serializer_class = serializers.IngridientSerializer


class UserSetPasswordViewset(views.APIView):

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Необходима авторизация'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        cur_user = request.user
        response_message = {}
        fields = ['old_password', 'new_password']
        for field in fields:
            if field not in request.data or not request.data[field]:
                response_message[field] = f'Проверьте поле {field}'
        if response_message:
            return Response(
                response_message,
                status=status.HTTP_400_BAD_REQUEST
            )
        if not cur_user.check_password(request.data['old_password']):
            return Response(
                {'detail': 'Неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cur_user.set_password(request.data['new_password'])
        cur_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddToFavoriteView(views.APIView):
    def post(self, request, recipe_id):
        if self.request.user.is_authenticated:
            user = self.request.user
            recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
            recipe_obj.favorites.add(user)
            return Response(
                {'detail': 'Объект добавлен в избранное!'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'Учетные данные не были предоставлены.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    def delete(self, request, recipe_id):
        if self.request.user.is_authenticated:
            user = self.request.user
            recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
            recipe_obj.favorites.remove(user)
            return Response(
                {'detail': 'Объект удален из избранного!'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'detail': 'Учетные данные не были предоставлены.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class SubscribeListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    pagination_class = pagination.DefaultPagination
    serializer_class = serializers.UserSupscriptionsSerializer

    def get_queryset(self):
        return user.objects.filter(subscriptions__subscriber=self.request.user).order_by('id')


class SubscribeView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, ]

    # def list(self, request, *args, **kwargs):
    #     pagination_class = pagination.DefaultPagination
    #     queryset = user.objects.filter(subscriptions__subscriber=request.user)
    #     serializer_class = serializers.UserSupscriptionsSerializer

    # def get(self, request, *args, **kwargs):
    #     subs = request.user.subscribers.all()
    #     data_store = {'results':{}}
    #     for user in subs:
    #         temp_user_data = serializers.UserSerializer(user.author, context={'request': request}).data
    #         temp_user_data['recipes'] = serializers.RecipeViewSerializer(
    #             request.user.recipes.all(),
    #             many=True,
    #             context={'request': request},
    #             fields=['id', 'name', 'image', 'cooking_time']
    #         ).data
    #         data_store['results'][user.author.username]=temp_user_data
    #     return Response(data_store, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(user, pk=self.kwargs['user_id'])
        if request.user == author or Subscription.objects.filter(
            author=author
        ).filter(subscriber=request.user).exists():
            return Response(
                {'error': 'Невозможно подписаться'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            Subscription.objects.create(author=author, subscriber=request.user)
            user_data = serializers.UserSerializer(
                author,
                context={'request': request}
            ).data
            user_data['recipes'] = serializers.RecipeSerializer(
                author.recipes.all(),
                many=True,
                context={'request': request},
                fields=['id', 'name', 'image', 'cooking_time']
            ).data
            return Response(user_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        author = get_object_or_404(user, pk=self.kwargs['user_id'])
        if not Subscription.objects.filter(author=author).filter(
            subscriber=request.user
        ).exists():
            return Response(
                {'error': 'Невозможно отписаться'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.filter(
            author=author, subscriber=request.user
        ).delete()
        return Response(
            {'detail': f'Отписка от {author.username} успешно оформлена'},
            status=status.HTTP_204_NO_CONTENT
        )


class AddToShoppingCartView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, ]

    # def get(self, request, recipe_id):
    #     cart = request.user.shopping_cart.first().recipes.all().order_by('id')
    #     cart_data = serializers.RecipeViewSerializer(cart, many=True, context={'request': request}).data
    #     return Response(cart_data)

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        shopping_cart = ShoppingCart.objects.get_or_create(
            customer=request.user
        )[0]

        if shopping_cart.recipes.filter(pk=recipe_id).exists():
            return Response(
                {'error': 'Рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart.recipes.add(recipe)
        recipe_data = serializers.RecipeSerializer(
            recipe,
            context={'request': request}
        ).data
        return Response(recipe_data, status=status.HTTP_200_OK)

    def delete(self, request, recipe_id):
        cart = get_object_or_404(
            ShoppingCart,
            pk=request.user.shopping_cart.first().id
        )
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if not cart.recipes.filter(pk=recipe_id).exists():
            return Response(
                {'error': 'Рецепт отсутствует в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart.recipes.remove(recipe)
        return Response(
            {'detail': 'Рецепт успешно удален из корзины'},
            status=status.HTTP_204_NO_CONTENT
        )