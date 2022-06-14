
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as dfilters
from food.models import Product, Recipe, ShoppingCart, Subscription, Tag
from rest_framework import (mixins, permissions,
                            status, views, viewsets)
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from . import pagination
from . import permissions as local_rights
from . import serializers
from . import filters as local_filters

user = get_user_model()


def check_fields(request, fields):
    response_message = {}
    for field in fields:
        if field not in request.data or not request.data[field]:
            response_message[field] = f'Проверьте поле {field}'
    if response_message:
        return response_message
    return None


class TokenLogin(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, *args, **kwargs):
        fields = ['email', 'password']
        check_errors = check_fields(request, fields)
        if check_errors:
            return Response(
                check_errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        cur_user = get_object_or_404(user, email=request.data['email'])
        if not cur_user.check_password(request.data['password']):
            return Response(
                {'password': 'Неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Token.objects.filter(user=cur_user).exists():
            return Response(
                {'auth_token': cur_user.auth_token.key},
                status=status.HTTP_201_CREATED
            )
        token = Token.objects.create(user=cur_user)
        return Response(
            {'auth_token': f'{token}'},
            status=status.HTTP_201_CREATED
        )


class TokenLogout(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        token = get_object_or_404(Token, user=request.user)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseViewSet(viewsets.ModelViewSet):
    """Базовая вьюха."""
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly | local_rights.IsAdmin
    ]
    pagination_class = pagination.DefaultPagination


class UserViewset(BaseViewSet):
    """Вьюха пользователей"""
    permission_classes = [
        local_rights.AllowPostOrReadOnly | local_rights.IsAdmin
    ]
    queryset = user.objects.all().order_by('id')
    serializer_class = serializers.UserSerializer

    def get_object(self):
        if 'me' in self.request.get_full_path():
            obj = self.request.user
        else:
            obj = get_object_or_404(user, pk=self.kwargs['pk'])
        print(obj)
        return obj

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

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод запрещен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class TagViewset(BaseViewSet):
    """Вьюха тэгов"""
    permission_classes = [local_rights.ReadOnly | local_rights.IsAdmin]
    pagination_class = None
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
    pagination_class = None
    permission_classes = [local_rights.ReadOnly | local_rights.IsAdmin]
    queryset = Product.objects.all().order_by('id')
    serializer_class = serializers.ProductSerializer
    filter_backends = (dfilters.DjangoFilterBackend, )
    filterset_class = local_filters.ProductFilter

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
    permission_classes = [
        local_rights.ReadAnyPostAuthChangeOwner | local_rights.IsAdmin
    ]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        request = self.request
        return Response(
            serializers.RecipeSerializer(
                self.request.user.recipes.last(),
                context={'request': request}).data
            )

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        for ingredient in instance.ingredients.all():
            ingredient.delete()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('id')
        if self.request.GET.get('is_favorited') == '1':
            queryset = queryset.filter(favorites__id=self.request.user.id)
            # queryset = self.request.user.favorites.all()
        if self.request.GET.getlist('tags'):
            queryset = queryset.filter(
                tags__slug__in=self.request.GET.getlist('tags')
            ).distinct()
        if self.request.GET.get('author'):
            queryset = queryset.filter(
                author__id=self.request.GET.get('author')
            )
        if self.request.GET.get('is_in_shopping_cart') == '1':
            queryset = queryset.filter(
                shopping_carts=self.request.user.shopping_cart
            )
        return queryset.order_by('id')


class UserSetPasswordViewset(views.APIView):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]

    def post(self, request):
        cur_user = request.user
        response_message = {}
        fields = ['current_password', 'new_password']
        for field in fields:
            if field not in request.data or not request.data[field]:
                response_message[field] = f'Проверьте поле {field}'
        if response_message:
            return Response(
                response_message,
                status=status.HTTP_400_BAD_REQUEST
            )
        if not cur_user.check_password(request.data['current_password']):
            return Response(
                {'detail': 'Неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cur_user.set_password(request.data['new_password'])
        cur_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddToFavoriteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]

    def post(self, request, recipe_id):
        cur_user = self.request.user
        recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
        if recipe_obj.favorites.filter(id=cur_user.id).exists():
            return Response(
                {'detail': 'Рецепт уже добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe_obj.favorites.add(cur_user)
        recipe_data = serializers.RecipeSerializer(
            recipe_obj,
            context={'request': request},
            fields=['id', 'name', 'image', 'cooking_time']
        ).data
        return Response(recipe_data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        cur_user = self.request.user
        recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
        if not recipe_obj.favorites.filter(id=cur_user.id).exists():
            return Response(
                {'detail': 'Рецепт отсутствует в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe_obj.favorites.remove(cur_user)
        return Response(
            {'detail': 'Объект удален из избранного!'},
            status=status.HTTP_204_NO_CONTENT
        )


class SubscribeListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]
    pagination_class = pagination.DefaultPagination
    serializer_class = serializers.UserSupscriptionsSerializer

    def get_queryset(self):
        return user.objects.filter(
            subscriptions__subscriber=self.request.user
        ).order_by('id')


class SubscribeView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]

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
            user_data = serializers.UserSupscriptionsSerializer(
                author,
                context={'request': request}
            )
            return Response(user_data.data, status=status.HTTP_201_CREATED)

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
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        shopping_cart, stats = ShoppingCart.objects.get_or_create(
            customer=request.user
        )

        if shopping_cart.recipes.filter(pk=recipe_id).exists():
            return Response(
                {'error': 'Рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart.recipes.add(recipe)
        recipe_data = serializers.RecipeSerializer(
            recipe,
            context={'request': request},
            fields=['id', 'name', 'image', 'cooking_time']
        ).data
        return Response(recipe_data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        cart = get_object_or_404(
            ShoppingCart,
            pk=request.user.shopping_cart.id
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


class ExportShoppingCart(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]

    def get(self, request):
        data = list(request.user.shopping_cart.recipes.all().values(
            'ingredients__product__name',
            'ingredients__product__measurement_unit'
        ).annotate(amount=Sum('ingredients__amount')))
        # sorted_data = sorted(
        #     data,
        #     key=lambda d: d['ingredients__product__name']
        # )
        with open(
            f'{request.user.username}_shopping_cart.txt',
            'w',
            encoding='utf-8'
        ) as file:
            file.write(
                f'Список покупок для {request.user.username}:'.encode('utf8')
            )
            file.write('\n')
            for product in data:
                file.write(
                    f"{product['ingredients__product__name']}"
                    f" ({product['ingredients__product__measurement_unit']})"
                    f" - {product['amount']}".encode('utf8')
                )
                file.write('\n')
            file.write('\n')
            file.write('Составлено с ❤ и FoodGram'.encode('utf8'))
        file = open(f'{request.user.username}_shopping_cart.txt', 'rb')
        response = FileResponse(
            file,
            filename=f'{request.user.username}_shopping_cart.txt'
        )
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(
                f'{request.user.username}_shopping_cart.txt'
            )
        )
        return response

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
