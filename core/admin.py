from django.contrib import admin
from .models import FoodItem, Order, CartItem, Tag, Rating

# Register your models here.
admin.site.register(Tag)
admin.site.register(FoodItem)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(Rating)