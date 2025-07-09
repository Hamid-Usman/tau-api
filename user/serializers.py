from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import User
from rest_framework.serializers import ModelSerializer

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'password')

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_staff')

class DashboardSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    orders_completed = serializers.IntegerField()
    top_ratings = serializers.IntegerField()
    total_ratings = serializers.IntegerField()
