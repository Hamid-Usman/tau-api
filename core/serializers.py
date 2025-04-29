from rest_framework import serializers
from .models import FoodItem, CartItem, Order, OrderItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()  # Add a custom field for total price

    class Meta:
        model = CartItem
        fields = ["id", "food_item", "customer", "quantity", "added_at", "total"]
        read_only_field = ["added_at"]
    
    def get_total(self, obj):
        # Calculate total price for the cart item
        return obj.quantity * obj.food_item.price
class OrderSerializer(serializers.ModelSerializer):
        class Meta:
            model = Order
            fields = ["id", "customer", "vendor", "order_date", "status", "total"]

class OrderItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "order", "food_item", "quantity", "price"]
        read_only_field = ["id", "order", "price"]