from django.contrib import admin
from .models import FoodItem, Order, OrderItem, CartItem, Tag, Rating, ReviewAgent

# Register your models here.
admin.site.register(Tag)
admin.site.register(FoodItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(Rating)
admin.site.register(ReviewAgent)