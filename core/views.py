# from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Tag, FoodItem, Rating, ReviewAgent, CartItem, Order, OrderItem
from .serializers import TagSerializer, FoodItemSerializer, RatingSerializer, CartSerializer, OrderSerializer, OrderCreateSerializer, OrderStatusSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from collections import defaultdict
from decimal import Decimal
from rest_framework.decorators import action
from paystackapi.transaction import Transaction
from rest_framework import status
# from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MenuFilter, RatingFilter
from rest_framework.exceptions import ValidationError
from services.prompts.ai_recommendation import handle_ai_recommendation
from services.prompts.food_description import handle_description_generation
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import ChatPromptTemplate
import threading


import uuid

# Create your views here.
class FoodViewSet(ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    parser_classes = (MultiPartParser, FormParser,)
    
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_class = MenuFilter
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not serializer.validated_data.get("description"):
            food_item = serializer.save(description="", description_generated=False)
            handle_description_generation(food_item.id)
            
            return Response({
                "Status": f"Generating description for {food_item.name} ",
                "id":food_item.id
            })
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    
    @action(detail=False, methods=['get'])
    def recommended_product_to_user(self, request):
        past_orders = OrderItem.objects.all()
        order_data = list(past_orders.values("food_item__name"))
        
        handle_ai_recommendation(order_data)
        return Response({"detail": "analysis working now..."})

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class RatingViewSet(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = RatingFilter
    
    # def perform_create(self, serializer):
    def perform_create(self, serializer):

        customer = self.request.user
        # order_item = serializer.validated_data.get("order_item")
        # order = serializer.validated_data.get("order")

        # if order_item.order != order:
        #     raise ValidationError("OrderItem does not belong to the specified Order.")

        # if Rating.objects.filter(order_item=order_item, customer=customer).exists():
        #     raise ValidationError("You have already rated this item.")

        serializer.save(customer=customer)
    
    @action(detail=False, methods=['get'])
    def ai_analysis(self, request):
        reviews = Rating.objects.all()
        if not reviews.exists():
            return Response("detail: No reviews")
        
        review_data = list(reviews.values("rating", "comment"))
        
        threading.Thread(
            target=self.generate_review_summary,
            args= (review_data,)
        ).start()
        return Response(
            {"status": "Working on review analysis"}
        )
    
    def generate_review_summary(self, reviews_data):
        try: 
            print("Analysing reviews...")
            
            llm = Ollama(model="mistral", temperature=0.7)
            
            prompt_template ="""
                    Provide detailed analysis for these food item reviews. highlight whats working, and possible areas to improve in:
                    {formatted_data}
            """
            formatted_data = {
                "/n".join(
                    f"Rating: {r["rating"]}/5 -- Comment: {r["comment"]}"
                    for r in reviews_data
                )
            }
            print("working")
            prompt = ChatPromptTemplate.from_template(prompt_template)
            chain = prompt | llm
            analysis = chain.invoke({"formatted_data": formatted_data})
            print("worked")
            
            ReviewAgent.objects.create(analysis=analysis)
            print("AI generated review saved")
            
        
        except Exception as e:
            print("failed")
        
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
        cart_items = CartItem.objects.filter(customer=customer).select_related('food_item') # It tells Django to perform a SQL join and fetch the related FoodItem objects for each cart item in the same database query
        serializer = CartSerializer(cart_items, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def delete_cart_item(self, request, pk=None):
        try:
            cart_item = CartItem.objects.get(id=pk, customer=request.user)
            cart_item.delete()
            return Response({"message": "Cart item deleted successfully"}, status=204)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_serializer_class(self):
        if self.action == 'partial_update':
            return OrderStatusSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        
        customer = request.user
        if not customer.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        
        cart_items = CartItem.objects.filter(customer=customer)
        cart_item_ids = request.data.get('cart_item_ids', [])
        delivery_location = request.data.get('delivery_location', '')
        
        if cart_item_ids:
            cart_items = cart_items.filter(id__in=cart_item_ids)

        if not cart_items.exists():
            return Response({"error": "No cart items found for this customer"}, status=400)

        if not delivery_location:
            return Response({"error": "Delivery location is required"}, status=400)

        # Calculate total
        total = Decimal('0.00')
        for cart_item in cart_items:
            total += cart_item.quantity * cart_item.food_item.price

        # Create order first
        order = Order.objects.create(
            customer=customer,
            total=total,
            status='Pending',
            delivery_location=delivery_location
        )

        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                food_item=cart_item.food_item,
                quantity=cart_item.quantity,
                price=cart_item.food_item.price,
                customer=customer
            )
        

        try:
            # Initialize Paystack payment
            reference = f"ORDER-{order.id}-{uuid.uuid4().hex[:6]}"
            response = Transaction.initialize(
                email=customer.email,
                amount=int(total * 100),  # Paystack uses amount in kobo
                reference=reference,
                callback_url="http://tau-bite.vercel.app/home/order",
                metadata={
                    'order_id': str(order.id),
                    'customer_id': str(customer.id),
                }
            )
            
            if not response.get('status'):
                return Response({"error": "Payment initialization failed"}, status=400)
            
            # Update order with payment reference
            order.payment_reference = reference
            order.save()
            cart_items.delete()
            
            return Response({
                "order_id": order.id,
                "payment_url": response['data']['authorization_url'],
                "reference": reference
            }, status=201)
            
        except Exception as e:
            order.status = 'failed'
            order.save()
            return Response({"error": str(e)}, status=500)
    
    # Override the list method to return all orders with their items / meant for admin view
    def list(self, request, *args, **kwargs):
        
        orders = Order.objects.all()

        data = []
        for order in orders:
            food_items = []
            total_sum = 0
            for item in order.items.all():
                item_total = float(item.price * item.quantity)
                total_sum += item_total
                food_items.append({
                    "order_id": item.id,
                    "food_id": item.food_item.id,
                    "name": item.food_item.name,
                    "price": float(item.food_item.price),
                    "quantity": item.quantity,
                    "price_at_order": item_total,
                })

            data.append({
                "id": order.id,  # Consistent field naming
                "status": order.status,
                "payment_reference": order.payment_reference,
                "food_items": food_items,
                "total_sum": total_sum,
            })
        return Response(data)

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
        
    
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        order = self.get_object()
        
        if order.status != 'pending':
            return Response({
                "status": order.status,
                "message": f"Order already {order.status}"
            })
        
        try:
            response = Transaction.verify(order.payment_reference)
            
            if response['data']['status'] == 'success':
                # Mark order as paid
                order.status = 'paid'
                order.save()
                
                # Clear the cart
                CartItem.objects.filter(customer=request.user).delete()
                
                return Response({
                    "status": "success",
                    "order": OrderSerializer(order).data
                })
            else:
                order.status = 'failed'
                order.save()
                return Response({
                    "status": "failed",
                    "message": "Payment verification failed"
                }, status=400)
                
        except Exception as e:
            order.status = 'failed'
            order.save()
            return Response({"error": str(e)}, status=500)
        customer = request.user
        if not customer.is_authenticated:
            print("User not authenticated") 
            return Response({"error": "Authentication required"}, status=401)
            

    # This action is for authenticated users to view their own orders
    @action(detail=False, methods=['get'], url_path="user-orders")
    def user_order(self, request, *args, **kwargs):
        customer = request.user
        if not customer.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
            
        orders = Order.objects.filter(customer=customer).prefetch_related('items__food_item')

        data = []
        for order in orders:
            food_items = []
            total_sum = 0
            for item in order.items.all():
                item_total = float(item.price * item.quantity)
                total_sum += item_total
                food_items.append({
                    "order_item_id": item.id,
                    "food_item_id": item.food_item.id,
                    "name": item.food_item.name,
                    "price": float(item.food_item.price),
                    "quantity": item.quantity,
                    "price_at_order": item_total,
                })

            data.append({
                "id": order.id,
                "status": order.status,
                "order_date": order.order_date,
                "order_time": order.order_time,
                "payment_reference": order.payment_reference,
                "food_items": food_items,
                "total_sum": total_sum,
            })
        return Response(data)
    
    
