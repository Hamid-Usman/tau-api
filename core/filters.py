import django_filters
from .models import FoodItem

class MenuFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    tags = django_filters.CharFilter(field_name='tags', lookup_expr='in')
    price = django_filters.CharFilter(field_name='price', lookup_expr="lte")
    
    class Meta:
        model = FoodItem
        fields = ['name', 'tags', 'price']