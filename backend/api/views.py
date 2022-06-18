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
from food.models import Product, Recipe, ShoppingCart, Subscription, Tag

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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        cur_user = self.request.user
        if (
            self.request.GET.get('is_favorited') == '1'
            and cur_user.is_authenticated
        ):
            queryset = cur_user.favorites.all()
        if self.request.GET.getlist('tags'):
            queryset = queryset.filter(
                tags__slug__in=self.request.GET.getlist('tags')
            ).distinct()
        if self.request.GET.get('author'):
            queryset = queryset.filter(
                author__id=self.request.GET.get('author')
            )
        if (
            self.request.GET.get('is_in_shopping_cart') == '1'
            and cur_user.is_authenticated
        ):
            queryset = queryset.filter(
                shopping_carts=cur_user.shopping_cart
            )
        return queryset.order_by('-published')


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
                {'errors': 'Рецепт уже добавлен в избранное'},
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
                {'errors': 'Рецепт отсутствует в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe_obj.favorites.remove(cur_user)
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class AddToShoppingCartView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        shopping_cart, stats = ShoppingCart.objects.get_or_create(
            customer=request.user
        )

        if shopping_cart.recipes.filter(pk=recipe_id).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен'},
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
                {'errors': 'Рецепт отсутствует в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExportShoppingCart(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated | local_rights.IsAdmin]

    def get(self, request):
        data = request.user.shopping_cart.recipes.all().values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('ingredients__ingredients__amount'))
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
