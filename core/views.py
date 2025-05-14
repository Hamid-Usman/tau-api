from django.shortcuts import render
from .models import FoodItem, CartItem, Order, OrderItem
from .serializers import FoodItemSerializer, CartSerializer, OrderSerializer
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
    queryset = CartItem.objects.all()
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        data = request.data # gets input data from the frontend
        try:
            food_item = FoodItem.objects.get(id=data.get('food_item')) # gets the id of the selected food item
        except FoodItem.DoesNotExist:
            return Response({'error': 'Food item not found.'}, status=404)
        #You can handle any additional logic here
        cart_item = CartItem.objects.create(
            customer=request.user,
            food_item=food_item, 
            quantity=data.get('quantity', 1)  # Default to 1 if not provided
        )
        return Response(CartSerializer(cart_item).data, status=201)

    def list(self, request, *args, **kwargs):
        customer = request.user
        cart_items = CartItem.objects.filter(customer=customer)
        serializer = CartSerializer(cart_items, many=True, context={'request': request})
        return Response(serializer.data)
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        customer = request.user

        cart_items = CartItem.objects.filter(
            customer=customer
        )

        if not cart_items.exists():
            return Response({"error": "No cart items found for this customer"}, status=400)

        order = Order.objects.create(customer=customer)

        total = Decimal('0.00')

        # Create the order

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


    def list(self, request, *args, **kwargs):
        """
        Override the default `list()` method to include food item details in the response.
        """
        customer = 2
        orders = Order.objects.filter(customer=customer).prefetch_related('items__food_item')

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
                "status": order.status,
                "food_items": food_items,
                "total_sum": total_sum
            })
        return Response(data)