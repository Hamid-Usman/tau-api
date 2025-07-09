from itertools import count
from django.db.models import Count, Prefetch
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from .models import User
from core.serializers import FoodItemSerializer
from core.models import FoodItem, Order, OrderItem, Rating
from .serializers import UserSerializer, DashboardSerializer
from rest_framework import viewsets
from rest_framework.response import Response
class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_staff', 'is_superuser', 'points')

class AdminViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    
    @action(
        detail=False,
        methods=["get"],
    )
    def dashboard(self, request, *args, **kwargs):
        total_orders = Order.objects.count()
        orders_completed = Order.objects.filter(status="Completed").count()
        
        top_rating = Rating.objects.filter(rating = 5).count()
        total_rating = Rating.objects.count()
        
        
        data = {
            "total_orders": total_orders,
            "orders_completed": orders_completed,
            "top_ratings": top_rating,
            "total_ratings": total_rating,
            # "top_orders": FoodItemSerializer(top_items, many=True).data
        }
        
        serializer = DashboardSerializer(data)
        
        return Response(serializer.data)
    
    @action(
        detail=False,
        methods=["get"],
        url_path="items-chart")
    def top_items(self, request, *args, **kwargs):
        top_items = FoodItem.objects.annotate(total_orders=Count('orderitem')).order_by('-total_orders')[:2]
        serializer = FoodItemSerializer(top_items, many=True)
        
        return Response(serializer.data)