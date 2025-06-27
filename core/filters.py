import django_filters
from .models import FoodItem, Rating

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
    
class RatingFilter(django_filters.FilterSet):
    order = django_filters.CharFilter(field_name='order__id', lookup_expr='exact')
    food_item = django_filters.CharFilter(field_name='order_item__food_item__name', lookup_expr='icontains')
    customer = django_filters.CharFilter(field_name='customer__username', lookup_expr='icontains')
    
    class Meta:
        model = Rating
        fields = ['order', 'food_item', 'customer']
    
    def filter_food_item(self, queryset, name, value):
        return queryset.filter(order_item__food_item__name__icontains=value)
    
    def filter_customer(self, queryset, name, value):
        return queryset.filter(customer__username__icontains=value)
    
    def filter_order(self, queryset, name, value):
        return queryset.filter(order__id=value)