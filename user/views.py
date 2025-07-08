from itertools import count
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from .models import User
from core.models import Order, Rating
from .serializers import UserSerializer, DashboardSerializer
from rest_framework import viewsets
from rest_framework.response import Response
class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_staff', 'is_superuser', 'points')

class AdminViewSet(viewsets.GenericViewSet):
    
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
        }
        
        serializer = DashboardSerializer(data)
        
        return Response(serializer.data)