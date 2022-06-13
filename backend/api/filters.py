from django_filters import FilterSet, rest_framework
from food.models import Product


class ProductFilter(FilterSet):
    name = rest_framework.CharFilter('name', 'icontains')

    class Meta:
        model = Product
        fields = ['name', ]
