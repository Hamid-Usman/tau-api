from backend.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()

routers.register(r'customer', views.CustomerViewSet, basename="customer")
urlpatterns = [
    path('', include(routers.urls))
]