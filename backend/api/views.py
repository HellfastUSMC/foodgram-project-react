from multiprocessing import context
from django.forms import ValidationError
from rest_framework import permissions, viewsets, views, status, filters # ПОИСК ПО СТРОКЕ
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from users.models import Subscribition

from .filters import TagFilter

from . import serializers, pagination, permissions as local_rights

from food.models import Tag, Product, Recipe, Ingridient

user = get_user_model()


class TokenLogout(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ref_str = RefreshToken.for_user(request.user)
        token = RefreshToken(ref_str)
        token.blacklist()
        return Response({'Logged out!'})


class BaseViewSet(viewsets.ModelViewSet):
    """Базовая вьюха."""
    #permission_classes = [IsAdmin | ReadOnly]
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitOffsetPagination
    #filter_backends = (filters.SearchFilter,) ПОИСК ПО СТРОКЕ
    #search_fields = ('slug',) ПОИСК ПО СТРОКЕ
    #lookup_field = 'slug' ПОИСК ПО СТРОКЕ


class UserViewset(BaseViewSet):
    """Вьюха пользователей"""
    permission_classes = [local_rights.IsAuthenticatedAndOwner]
    queryset = user.objects.all()
    serializer_class = serializers.UserSerializer


class TagViewset(BaseViewSet):
    """Вьюха тэгов"""
    ordering_fields = ['slug', ]
    ordering = ['slug']
    serializer_class = serializers.TagSerializer

    def update(self, request, *args, **kwargs):
        return Response({'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        slug_values = self.request.GET.getlist('slug')
        if slug_values:
            queryset = Tag.objects.filter(slug__in=slug_values)
            print(slug_values)
        else:
            queryset = Tag.objects.all()
        return queryset


class ProductViewset(BaseViewSet):
    """Вьюха продуктов"""
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    def update(self, request, *args, **kwargs):
        return Response({'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({'Метод запрещен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# class UnitViewset(BaseViewSet):
#     """Вьюха единиц измерения"""
#     queryset = Unit.objects.all()
#     serializer_class = serializers.UnitSerializer


class RecipeViewset(BaseViewSet):
    """Вьюха рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = [local_rights.IsAuthenticatedAndOwner, ]
    #filter_backends = [DjangoFilterBackend, ]
    #filterset_fields = ['author', 'tags', ]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            #return Response({'Необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
            raise ValidationError('Требуется авторизация')

    def get_queryset(self):
        is_favorited = self.request.GET.get('is_favorited', None)
        tags = self.request.GET.getlist('tags', None)
        author = get_object_or_404(user, pk=self.request.GET.get('author', None))
        if is_favorited == '1':
            queryset = self.request.user.favorites.filter(tags__id__in=tags, author=author)
            print('new_qs',queryset)
        else:
            queryset = Recipe.objects.filter(tags__id__in=tags, author=author)
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.RecipeViewSerializer
        else:
            return serializers.RecipeSerializer


class IngridientViewset(BaseViewSet):
    """Вьюха ингридиентов"""
    queryset = Ingridient.objects.all()
    serializer_class = serializers.IngridientSerializer


class UserMeViewset(viewsets.ViewSet):
    def retrieve(self, request):
        queryset = user.objects.all()
        me = get_object_or_404(queryset, pk=request.user.id)
        serializer = serializers.UserSerializer(me, context={'request': request})
        return Response(serializer.data)


class UserSetPasswordViewset(views.APIView):

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            cur_user = request.user
            if 'old_password' not in request.data or not len(request.data['old_password']):
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
            return Response({'Объект добавлен в избранное!'}, status=status.HTTP_200_OK)
        else:
            return Response({'Учетные данные не были предоставлены.'}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, recipe_id):
        if self.request.user.is_authenticated:
            user = self.request.user
            recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
            recipe_obj.favorites.remove(user)
            return Response({'Объект удален из избранного!'}, status=status.HTTP_200_OK)
        else:
            return Response({'Учетные данные не были предоставлены.'}, status=status.HTTP_401_UNAUTHORIZED)


class SubscribeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(user, pk=self.kwargs['user_id'])
        if request.user == author or Subscribition.objects.filter(author=author).filter(subscriber=request.user).exists():
            return Response({'Невозможно подписаться'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Subscribition.objects.create(author=author, subscriber=request.user)
            user_data = serializers.UserSerializer(author, context={'request': request}).data
            user_data['recipes'] = serializers.RecipeViewSerializer(
                author.my_recipes.all(),
                many=True,
                context={'request': request}
            ).data
            #return Response({f'Подписка на {author.username} успешно оформлена'})
            return Response(user_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        author = get_object_or_404(user, pk=self.kwargs['user_id'])
        if not Subscribition.objects.filter(author=author).filter(subscriber=request.user).exists():
            return Response({'Невозможно отписаться'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Subscribition.objects.filter(author=author, subscriber=request.user).delete()
            return Response({f'Отписка от {author.username} успешно оформлена'}, status=status.HTTP_204_NO_CONTENT)
