import django_filters
from .models import FoodItem

class MenuFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    tags = django_filters.CharFilter(method='filter_tags')  # Custom method
    price = django_filters.NumberFilter(field_name='price', lookup_expr="lte")
    
    class Meta:
        model = FoodItem
        fields = ['name', 'tags', 'price']
    
    def filter_tags(self, queryset, name, value):
        # Handle both single tag and multiple tags
        if value:
            tag_ids = value.split(',')  # Split comma-separated values
            return queryset.filter(tags__in=tag_ids)
        return queryset