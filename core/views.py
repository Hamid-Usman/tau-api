from django.shortcuts import render
from .models import FoodItem, CartItem, Order, OrderItem
from user.models import Vendor
from .serializers import FoodItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from collections import defaultdict
from decimal import Decimal
from django.shortcuts import get_object_or_404
# Create your views here.

class FoodViewSet(ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer

class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CartItem.objects.none()

        customer = self.request.user.customer
        queryset = CartItem.objects.filter(customer=customer)

        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            queryset = queryset.filter(food_item__vendor__id=vendor_id)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        Group cart items by vendor, or return items for a specific vendor if 'vendor' query param is given.
        """
        cart_items = self.get_queryset()

        # If filtering by a specific vendor, return a single group
        vendor_id = request.query_params.get('vendor')
        if vendor_id:
            vendor = get_object_or_404(Vendor, id=vendor_id)
            total = sum(
                item.quantity * item.food_item.price for item in cart_items
            )
            return Response({
                "vendor": vendor.id,
                "items": CartSerializer(cart_items, many=True).data,
                "total_price": total,
            })

        # Otherwise, group cart items by vendor
        vendor_totals = defaultdict(lambda: Decimal('0.0'))
        cart_items_by_vendor = defaultdict(list)

        for cart_item in cart_items:
            vendor = cart_item.food_item.vendor
            cart_items_by_vendor[vendor.id].append(cart_item)
            vendor_totals[vendor.id] += cart_item.quantity * cart_item.food_item.price

        vendor_cart_data = {}
        for vendor_id, items in cart_items_by_vendor.items():
            vendor_cart_data[vendor_id] = {
                "vendor": vendor_id,
                "items": CartSerializer(items, many=True).data,
                "total_price": vendor_totals[vendor_id],
            }

        return Response(vendor_cart_data)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from decimal import Decimal
from .models import Order, OrderItem, CartItem, Vendor
from .serializers import OrderSerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        vendor_id = request.data.get('vendor')

        if not vendor_id:
            return Response({"error": "Vendor ID is required"}, status=400)

        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)

        customer = request.user.customer

        # Get all cart items for this vendor and customer
        cart_items = CartItem.objects.filter(
            customer=customer,
            food_item__vendor__id=vendor_id
        )

        if not cart_items.exists():
            return Response({"error": "No cart items found for this vendor"}, status=400)

        total = Decimal('0.00')
        vendor = cart_items.first().food_item.vendor

        # Create the order
        order = Order.objects.create(customer=customer, vendor=vendor)

        # Create OrderItems and calculate total
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                food_item=cart_item.food_item,
                quantity=cart_item.quantity,
                price=cart_item.food_item.price,
            )
            total += cart_item.quantity * cart_item.food_item.price

        order.total = total
        order.save()

        # Remove cart items after placing order
        cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=201)
class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def list(self, request, *args, **kwargs):
        """
        Override the default `list()` method to include food item details in the response.
        """
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer).prefetch_related('items__food_item', 'vendor')

        data = []
        for order in orders:
            food_items = []
            total_sum = 0
            for item in order.items.all():
                item_total = float(item.price * item.quantity)
                total_sum += item_total
                food_items.append({
                    "id": item.food_item.id,
                    "name": item.food_item.name,
                    "price": float(item.food_item.price),
                    "quantity": item.quantity,
                    "price_at_order": item_total,
                })

            data.append({
                "order_id": order.id,
                "vendor": order.vendor.restaurant_name,
                "status": order.status,
                "food_items": food_items,
                "total_sum": total_sum
            })
        return Response(data)