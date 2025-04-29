from backend.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()

routers.register(r'customer', views.CustomerViewSet, basename="customer")
routers.register(r'vendor', views.VendorViewSet, basename="vendor")

urlpatterns = [
    path('', include(routers.urls))
]