from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
from django.urls import path, include

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("admin/order/<int:order_id>", OrderDetailView.as_view(), name="manage_order"),
]
