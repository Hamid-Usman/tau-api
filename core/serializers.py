from rest_framework import serializers
from .models import FoodItem, CartItem, OrderItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "food_item", "quantity", "added_at"]
        read_only_field = ["added_at"]