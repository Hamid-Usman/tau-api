from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register("", views.AdminViewSet, basename="admin")

urlpatterns = [
    path("me/", include(router.urls))
]