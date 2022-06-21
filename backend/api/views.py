from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as dfilters
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from . import (
    filters as local_filters, pagination, permissions as local_rights,
    serializers, utils,
)
from food.models import Product, Recipe, Subscription, Tag, ShoppingCart

user = get_user_model()


class TokenLogin(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, *args, **kwargs):
        fields = ['email', 'password']
        check_errors = utils.check_fields(request, fields)
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


class UserViewset(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вьюха пользователей"""
    permission_classes = [
        local_rights.AllowPostOrReadOnly | local_rights.IsAdmin
    ]
    pagination_class = pagination.DefaultPagination
    queryset = user.objects.all().order_by('id')
    serializer_class = serializers.UserSerializer

    def get_object(self):
        if 'me' in self.request.get_full_path():
            obj = self.request.user
        else:
            obj = get_object_or_404(user, pk=self.kwargs['pk'])
        return obj


class TagViewset(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вьюха тэгов"""
    permission_classes = [local_rights.ReadOnly | local_rights.IsAdmin]
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ProductViewset(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вьюха продуктов"""
    pagination_class = None
    permission_classes = [local_rights.ReadOnly | local_rights.IsAdmin]
    queryset = Product.objects.all().order_by('id')
    serializer_class = serializers.ProductSerializer
    filter_backends = (dfilters.DjangoFilterBackend, )
    filterset_class = local_filters.ProductFilter


class RecipeViewset(viewsets.ModelViewSet):
    """Вьюха рецептов"""
    serializer_class = serializers.RecipeSerializer
    pagination_class = pagination.DefaultPagination
    permission_classes = [
        local_rights.ReadAnyPostAuthChangeOwner | local_rights.IsAdmin
    ]
    filter_backends = (dfilters.DjangoFilterBackend, )
    filter_class = local_filters.RecipeFilter
    queryset = Recipe.objects.all().order_by('-published')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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


class SubscribeListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]
    pagination_class = pagination.DefaultPagination
    serializer_class = serializers.UserSupscriptionsSerializer

    def get_queryset(self):
        return user.objects.filter(
            subscriptions__subscriber=self.request.user
        ).order_by('id')


class PostDeleteMixin():
    def post(self, request, recipe_id):
        cur_user = self.request.user
        recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
        if self.view_name == 'shopping_carts':
            cur_filter = 'shopping_carts'
            cur_value = ShoppingCart.objects.get_or_create(customer=cur_user)
        if self.view_name == 'favorites':
            cur_filter = 'favorites'
            cur_value = cur_user
        if Recipe.objects.filter(
            **{cur_filter: cur_value},
            pk=recipe_id
        ).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if self.view_name == 'favorites':
            recipe_obj.favorites.add(cur_value)
        if self.view_name == 'shopping_carts':
            cur_value.recipes.add(recipe_obj)

        recipe_data = serializers.RecipeSerializer(
            recipe_obj,
            context={'request': request},
            fields=['id', 'name', 'image', 'cooking_time']
        ).data
        return Response(recipe_data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        cur_user = request.user
        recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
        if self.view_name == 'shopping_carts':
            cur_value = cur_user.shopping_cart
        if self.view_name == 'favorites':
            cur_value = cur_user
        if not Recipe.objects.filter(
            **{self.view_name: cur_value},
            pk=recipe_id
        ).exists():
            return Response(
                {'errors': 'Рецепт отсутствует и не может быть удален.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if self.view_name == 'favorites':
            recipe_obj.favorites.remove(cur_user)
        if self.view_name == 'shopping_carts':
            cur_value.recipes.remove(recipe_obj)

        return Response(status=status.HTTP_204_NO_CONTENT)


class AddToFavoriteView(views.APIView, PostDeleteMixin):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]
    view_name = 'favorites'


class AddToShoppingCartView(viewsets.ViewSet, PostDeleteMixin):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]
    view_name = 'shopping_carts'


class SubscribeView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(user, pk=self.kwargs['user_id'])
        if request.user == author or Subscription.objects.filter(
            author=author
        ).filter(subscriber=request.user).exists():
            return Response(
                {'errors': 'Невозможно подписаться'},
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
                {'errors': 'Невозможно отписаться'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.filter(
            author=author, subscriber=request.user
        ).delete()
        return Response(
            {'detail': f'Отписка от {author.username} успешно оформлена'},
            status=status.HTTP_204_NO_CONTENT
        )


class ExportShoppingCart(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]

    def get(self, request):
        data = request.user.shopping_cart.recipes.all().values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('ingredient__amount'))
        text = []
        text.append(f'Список покупок для {request.user.username}:\n')
        for product in data:
            text.append(f"{product['ingredients__name']}"
                        f" ({product['ingredients__measurement_unit']})"
                        f" - {product['amount']}")
        text.append('\nСоставлено с ❤ и FoodGram')
        ready_text = '\n'.join(text)
        response = HttpResponse(
            ready_text,
            content_type="text/plain,charset=utf8"
        )
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(
                f'{request.user.username}_shopping_cart.txt'
            )
        )
        return response
