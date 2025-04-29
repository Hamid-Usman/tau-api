from djoser.serializers import UserCreateSerializer
from .models import User, Customer, Vendor
from rest_framework.serializers import ModelSerializer

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'password')

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class VendorSerializer(ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'