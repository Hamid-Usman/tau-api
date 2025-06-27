from rest_framework import serializers
from .models import Tag, FoodItem, Rating, CartItem, Order, OrderItem, Tag

from django.db.models import Avg

class RatingSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source="order_item_id.food_item.name", read_only=True)
    
    class Meta:
        model = Rating
        fields = ["id", "order", "order_item", "food_item_name", "rating", "customer",
                "comment", "created_at"]
        read_only_fields = [ "customer" ]
    def validate(self, data):
        order = data.get('order')
        order_item = data.get('order_item')
        if order_item and order and order_item.order != order:
            raise serializers.ValidationError("OrderItem does not belong to the specified Order.")
        return data

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        
class FoodItemSerializer(serializers.ModelSerializer):
    
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='tag',
        queryset=Tag.objects.all()  # Needed for write support
    )
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FoodItem
        fields = ["id", "name", "image", "price", "description", "tags", "average_rating", "rating_count"]
        
    def get_average_rating(self, obj):
        average = Rating.objects.filter(order_item__food_item=obj).aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(average, 1) if average is not None else 0
    
    def get_rating_count(self, obj):
        ratings = Rating.objects.filter(order_item__food_item=obj).count()
        return ratings

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
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)
    food_item_id = serializers.PrimaryKeyRelatedField(source='food_item', read_only=True)
    is_rated = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item_id', 'food_item_name', 'quantity', 'price', 'is_rated']

    def get_is_rated(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.ratings.filter(customer=request.user).exists()
        return False
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'order_time', 'status', 'total', 'delivery_location', 'items']
        read_only_fields = ['id', 'order_date', 'order_time', 'status', 'total', 'items']

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']