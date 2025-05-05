from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import CustomerSerializer, VendorSerializer
from .models import Customer, Vendor, User

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
