from django.shortcuts import render
from .models import FoodItem, CartItem
from .serializers import FoodItemSerializer, CartSerializer
from rest_framework.viewsets import ModelViewSet

# Create your views here.

class FoodViewSet(ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer

class CartViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartSerializer