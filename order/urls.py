from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
from django.urls import path

urlpatterns = [
    path("order/", OrderCreateView.as_view(), name="create_order"),
    path("order/list/", OrderListView.as_view(), name="order_list"),
    path("admin/order/<int:order_id>", OrderDetailView.as_view(), name="manage_order"),
]
