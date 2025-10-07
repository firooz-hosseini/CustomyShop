from django_filters import rest_framework as filters
from .models import StoreItem, Store
from products.models import Category


class StoreItemFilter(filters.FilterSet):
    category = filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        method='filter_category',
        label='Category',
        required=False,
    )
    store = filters.ModelChoiceFilter(
        queryset=Store.objects.all(),
        label='Store',
        required=False,
    )
    min_price = filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Price is greater than or equal to',
        required=False,
    )
    max_price = filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Price is less than or equal to',
        required=False,
    )
    is_active = filters.BooleanFilter(
        label='Is active',
        required=False,
    )

    class Meta:
        model = StoreItem
        fields = ['store', 'category', 'is_active', 'min_price', 'max_price']

    def filter_category(self, queryset, name, value):
        category_ids = self.get_descendant_ids(value)
        return queryset.filter(product__category__id__in=category_ids)

    def get_descendant_ids(self, category):
        ids = [category.id]
        for child in category.children.all():
            ids.extend(self.get_descendant_ids(child))
        return ids
