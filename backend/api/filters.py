from django_filters import FilterSet, rest_framework
from food.models import Product, Recipe, Tag


class ProductFilter(FilterSet):
    name = rest_framework.CharFilter('name', 'icontains')

    class Meta:
        model = Product
        fields = ['name', ]


class RecipeFilter(FilterSet):
    tags = rest_framework.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = rest_framework.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        if value:
            queryset = queryset.filter(favorites=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                shopping_carts=self.request.user.shopping_cart
            )
        return queryset
