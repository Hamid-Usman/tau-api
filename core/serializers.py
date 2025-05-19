from rest_framework import serializers
from .models import FoodItem, CartItem, Order, OrderItem, Tag


class FoodItemSerializer(serializers.ModelSerializer):
    
    
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='tag',
        queryset=Tag.objects.all()  # Needed for write support
    )
    class Meta:
        model = FoodItem
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    food_item = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "food_item", "customer", "quantity", "added_at", "total"]
        read_only_fields = ["added_at"]

    def get_food_item(self, obj):
        request = self.context.get("request")
        image_url = (
            request.build_absolute_uri(obj.food_item.image.url)
            if request and obj.food_item and obj.food_item.image
            else None
        )
        return {
            "id": obj.food_item.id,
            "name": obj.food_item.name,
            "price": float(obj.food_item.price),
            "image": image_url
        }

    def get_total(self, obj):
        return float(obj.quantity * obj.food_item.price)
class OrderCreateSerializer(serializers.Serializer):
    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    
class OrderItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['food_item', 'quantity', 'price']
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'status', 'total', 'items']
        read_only_fields = ['id', 'order_date', 'status', 'total', 'items']
