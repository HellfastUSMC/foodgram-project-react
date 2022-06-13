from django_filters import FilterSet, rest_framework
#from rest_framework import filters
from food.models import Product


class ProductFilter(FilterSet):
    name = rest_framework.CharFilter('name', 'icontains')
    class Meta:
        model = Product
        fields = ['name',]


# class CustomSearchFilter(filters.SearchFilter):
#     def get_search_fields(self, view, request):
#         if request.query_params.get('name'):
#             return ['name']
#         return super().get_search_fields(view, request)