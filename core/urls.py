from backend.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()

routers.register(r'food', views.FoodViewSet, basename="food")
routers.register(r'cart', views.CartViewSet, basename="cart")
routers.register(r'rating', views.RatingViewSet, basename="rating")
routers.register(r'order', views.OrderViewSet, basename="order")
urlpatterns = [
    path("", include(routers.urls))
]