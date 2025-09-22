from django_filters import rest_framework as filters
from .models import Product, Category

class ProductFilter(filters.FilterSet):
    category = filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        method='filter_category'
    )

    class Meta:
        model = Product
        fields = ['category']

    def filter_category(self, queryset, name, value):
        category_ids = self.get_descendant_ids(value)
        return queryset.filter(category__id__in=category_ids)

    def get_descendant_ids(self, category):
        ids = [category.id]
        for child in category.children.all():
            ids.extend(self.get_descendant_ids(child))
        return ids
