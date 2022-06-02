from django_filters import FilterSet, ModelMultipleChoiceFilter

from food.models import Tag


class TagFilter(FilterSet):
    slug = ModelMultipleChoiceFilter(queryset=Tag.objects.all())

    class Meta:
        model = Tag
        fields = ['slug']