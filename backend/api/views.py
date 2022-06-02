from rest_framework import permissions, viewsets, views # filters ПОИСК ПО СТРОКЕ
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .filters import TagFilter

from . import serializers, pagination

from food.models import Tag, Product, Recipe, Ingridient

user = get_user_model()


class TokenLogout(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ref_str = RefreshToken.for_user(request.user)
        print(ref_str)
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
    queryset = user.objects.all()
    serializer_class = serializers.UserSerializer


class TagViewset(BaseViewSet):
    """Вьюха тэгов"""
    ordering_fields = ['slug', ]
    ordering = ['slug']
    serializer_class = serializers.TagSerializer

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


# class UnitViewset(BaseViewSet):
#     """Вьюха единиц измерения"""
#     queryset = Unit.objects.all()
#     serializer_class = serializers.UnitSerializer


class RecipeViewset(BaseViewSet):
    """Вьюха рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer


class IngridientViewset(BaseViewSet):
    """Вьюха ингридиентов"""
    queryset = Ingridient.objects.all()
    serializer_class = serializers.IngridientSerializer


class UserMeViewset(viewsets.ViewSet):
    def retrieve(self, request):
        queryset = user.objects.all()
        me = get_object_or_404(queryset, pk=request.user.id)
        serializer = serializers.UserSerializer(me)
        return Response(serializer.data)
