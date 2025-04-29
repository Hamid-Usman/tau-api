from django.shortcuts import render
from .models import FoodItem, CartItem, Order, OrderItem
from .serializers import FoodItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from collections import defaultdict
from decimal import Decimal
# Create your views here.

class FoodViewSet(ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer

class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CartItem.objects.none()  # Return an empty queryset for anonymous users
        customer = self.request.user.customer
        return CartItem.objects.filter(customer=customer)

    def list(self, request, *args, **kwargs):
        """
        Override the default `list()` method to group cart items by vendor
        """
        # Get all cart items for the logged-in customer
        cart_items = self.get_queryset()

        # Group cart items by vendor
        vendor_totals = defaultdict(lambda: Decimal('0.0'))
        cart_items_by_vendor = defaultdict(list)
        for cart_item in cart_items:
            vendor = cart_item.food_item.vendor
            if vendor.id not in cart_items_by_vendor:
                cart_items_by_vendor[vendor.id] = []
            cart_items_by_vendor[vendor.id].append(cart_item)
            vendor_totals[vendor.id] += cart_item.quantity * cart_item.food_item.price

        # Serialize cart items grouped by vendor
        vendor_cart_data = {}
        for vendor_id, items in cart_items_by_vendor.items():
            vendor_cart_data[vendor_id] = {
                "items": CartSerializer(items, many=True).data,
                "total_price": vendor_totals[vendor_id],
            }

        return Response(vendor_cart_data)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        """
        Override the default `create()` method to initialize orders for multiple vendors.
        """
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)

        customer = request.user.customer
        cart_items = CartItem.objects.filter(customer=customer)

        if not cart_items.exists():
            return Response({"error": "No items in the cart"}, status=400)

        # Group cart items by vendor
        orders = []
        cart_items_by_vendor = {}
        for cart_item in cart_items:
            vendor = cart_item.food_item.vendor
            if vendor not in cart_items_by_vendor:
                cart_items_by_vendor[vendor] = []
            cart_items_by_vendor[vendor].append(cart_item)

        # Create an order for each vendor
        for vendor, items in cart_items_by_vendor.items():
            order = Order.objects.create(customer=customer, vendor=vendor)
            for cart_item in items:
                OrderItem.objects.create(
                    order=order,
                    food_item=cart_item.food_item,
                    quantity=cart_item.quantity,
                    price=cart_item.food_item.price,
                )
            orders.append(order)

        # Clear the cart after creating the orders
        cart_items.delete()

        # Serialize the created orders
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=201)
class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer