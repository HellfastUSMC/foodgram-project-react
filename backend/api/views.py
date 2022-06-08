from django.forms import ValidationError
from rest_framework import permissions, viewsets, views, status, filters, mixins # ПОИСК ПО СТРОКЕ
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .filters import TagFilter

from . import serializers, pagination, permissions as local_rights

from food.models import Tag, Product, Recipe, Ingridient, Subscription, ShoppingCart

user = get_user_model()


class TokenLogout(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ref_str = RefreshToken.for_user(request.user)
        token = RefreshToken(ref_str)
        token.blacklist()
        return Response({'detail': 'Logged out!'})


class BaseViewSet(viewsets.ModelViewSet):
    """Базовая вьюха."""
    #permission_classes = [IsAdmin | ReadOnly]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = pagination.DefaultPagination
    #filter_backends = (filters.SearchFilter,) ПОИСК ПО СТРОКЕ
    #search_fields = ('slug',) ПОИСК ПО СТРОКЕ
    #lookup_field = 'slug' ПОИСК ПО СТРОКЕ


class UserViewset(BaseViewSet):
    """Вьюха пользователей"""
    permission_classes = [local_rights.IsAuthenticatedAndOwner]
    queryset = user.objects.all().order_by('id')
    serializer_class = serializers.UserSerializer


class TagViewset(BaseViewSet):
    """Вьюха тэгов"""
    #ordering_fields = ['slug', ]
    #ordering = ['slug']
    serializer_class = serializers.TagSerializer

    def update(self, request, *args, **kwargs):
        return Response({'detail': 'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({'detail': 'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        slug_values = self.request.GET.getlist('slug')
        if slug_values:
            queryset = Tag.objects.filter(slug__in=slug_values).order_by('id')
            print(slug_values)
        else:
            queryset = Tag.objects.all().order_by('id')
        return queryset


class ProductViewset(BaseViewSet):
    """Вьюха продуктов"""
    queryset = Product.objects.all().order_by('id')
    serializer_class = serializers.ProductSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    def update(self, request, *args, **kwargs):
        return Response({'detail': 'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({'detail': 'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewset(BaseViewSet):
    """Вьюха рецептов"""
    #queryset = Recipe.objects.all().order_by('id')
    serializer_class = serializers.RecipeSerializer
    permission_classes = [local_rights.IsAuthenticatedAndOwner, ]
    
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(serializers.RecipeViewSerializer(self.request.user.recipes.last(), context={'request': self.request}).data)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('id')
        if self.request.GET.get('is_favorited') == '1':
            queryset = queryset.filter(favorites__id=self.request.user.id)
        if self.request.GET.getlist('tags'):
            queryset = queryset.filter(tags__id__in=self.request.GET.getlist('tags'))
        if self.request.GET.get('author'):
            queryset = queryset.filter(author__id=self.request.GET.get('author'))
        return queryset.order_by('id')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.RecipeViewSerializer
        else:
            return serializers.RecipeSerializer


class IngridientViewset(BaseViewSet):
    """Вьюха ингридиентов"""
    queryset = Ingridient.objects.all().order_by('id')
    serializer_class = serializers.IngridientSerializer


class UserMeViewset(viewsets.ViewSet):
    def retrieve(self, request):
        me = get_object_or_404(user.objects.all(), pk=request.user.id)
        serializer = serializers.UserSerializer(me, context={'request': request})
        return Response(serializer.data)


class UserSetPasswordViewset(views.APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            cur_user = request.user
            if 'old_password' not in request.data or not cur_user.check_password(request.data['old_password']):
                return Response({'detail': 'Неверный пароль или отсутствует поле old_password'}, status=status.HTTP_403_FORBIDDEN)
            else:
                if 'new_password' not in request.data or len(request.data['new_password']) < 3:
                    return Response({'detail': 'Поле new_password отсутствует или его значение менее 3 символов'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    cur_user.set_password(request.data['new_password'])
                    cur_user.save()
                    return Response({'detail': 'Пароль успешно изменен'}, status=status.HTTP_200_OK)


class AddToFavoriteView(views.APIView):
    def post(self, request, recipe_id):
        if self.request.user.is_authenticated:
            user = self.request.user
            recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
            recipe_obj.favorites.add(user)
            return Response({'detail': 'Объект добавлен в избранное!'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Учетные данные не были предоставлены.'}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, recipe_id):
        if self.request.user.is_authenticated:
            user = self.request.user
            recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
            recipe_obj.favorites.remove(user)
            return Response({'detail': 'Объект удален из избранного!'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Учетные данные не были предоставлены.'}, status=status.HTTP_401_UNAUTHORIZED)


class SubscribeListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    pagination_class = pagination.DefaultPagination
    serializer_class = serializers.UserSupscriptionsSerializer

    def get_queryset(self):
        return user.objects.filter(subscriptions__subscriber=self.request.user)


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
        if request.user == author or Subscription.objects.filter(author=author).filter(subscriber=request.user).exists():
            return Response({'detail': 'Невозможно подписаться'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Subscription.objects.create(author=author, subscriber=request.user)
            user_data = serializers.UserSerializer(author, context={'request': request}).data
            user_data['recipes'] = serializers.RecipeViewSerializer(
                author.recipes.all(),
                many=True,
                context={'request': request},
                fields=['id', 'name', 'image', 'cooking_time']
            ).data
            return Response(user_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        author = get_object_or_404(user, pk=self.kwargs['user_id'])
        if not Subscription.objects.filter(author=author).filter(subscriber=request.user).exists():
            return Response({'detail': 'Невозможно отписаться'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Subscription.objects.filter(author=author, subscriber=request.user).delete()
            return Response({'detail': f'Отписка от {author.username} успешно оформлена'}, status=status.HTTP_204_NO_CONTENT)


class AddToShoppingCartView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, ]

    # def get(self, request, recipe_id):
    #     cart = request.user.shopping_cart.first().recipes.all().order_by('id')
    #     cart_data = serializers.RecipeViewSerializer(cart, many=True, context={'request': request}).data
    #     return Response(cart_data)

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        shopping_cart = ShoppingCart.objects.get_or_create(customer=request.user)[0]
        if shopping_cart.recipes.filter(pk=recipe_id).exists():
            return Response({'detail': 'Рецепт уже добавлен'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            shopping_cart.recipes.add(recipe)
            recipe_data = serializers.RecipeViewSerializer(recipe, context={'request': request}).data
            return Response(recipe_data, status=status.HTTP_200_OK)

    def delete(self, request, recipe_id):
        cart = get_object_or_404(ShoppingCart, pk=request.user.shopping_cart.first().id)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not cart.recipes.filter(pk=recipe_id).exists():
            return Response({'detail': 'Рецепт отсутствует в корзине'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            cart.recipes.remove(recipe)
            return Response({'detail': 'Рецепт успешно удален из корзины'}, status=status.HTTP_204_NO_CONTENT)