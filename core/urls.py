from backend.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()

routers.register(r'food', views.FoodViewSet, basename="food")
routers.register(r'cart', views.CartViewSet, basename="cart")
routers.register(r'order', views.OrderViewSet, basename="order")
routers.register(r'order-item', views.OrderItemViewSet, basename="order-item")

urlpatterns = [
    path("", include(routers.urls))
]