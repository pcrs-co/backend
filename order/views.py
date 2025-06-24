from rest_framework.permissions import AllowAny, IsAuthenticated
from login_and_register.models import CustomUser, Vendor
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import OrderSerializer
from vendor.models import Product
from .models import Order


class OrderCreateView(generics.CreateAPIView):
    """
    Handles creating a new order (POST). Replaces the old OrderView post method.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Associate the order with the logged-in user.
        serializer.save(user=self.request.user)


class OrderListView(generics.ListAPIView):
    """
    Returns a list of orders based on the user's role.
    This replaces the old APIView and is more standard.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Order.objects.all().order_by("-created_at")
        elif hasattr(user, "vendor"):
            # A vendor sees all orders for their products.
            return Order.objects.filter(vendor=user.vendor).order_by("-created_at")
        else:
            # A customer sees only their own orders.
            return Order.objects.filter(user=user).order_by("-created_at")


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles Retrieve (GET), Update (PUT/PATCH for actions), and Delete (DELETE) for a single order.
    This replaces the complex OrderManagementView.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only interact with orders relevant to them.
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        elif hasattr(user, "vendor"):
            # A vendor can see any order for their products.
            return Order.objects.filter(vendor=user.vendor)
        # A customer can only see their own orders.
        return Order.objects.filter(user=user)

    def perform_update(self, serializer):
        # --- Pushing for Errors: Add strict permission checks for actions ---
        order = self.get_object()
        action = serializer.validated_data.get("action")

        if action == "confirm":
            # Only the vendor associated with the order can confirm it.
            if (
                not hasattr(self.request.user, "vendor")
                or self.request.user.vendor != order.vendor
            ):
                raise permissions.PermissionDenied(
                    "You are not the vendor for this order."
                )

        elif action == "cancel":
            # Only the user who placed the order can cancel it.
            if self.request.user != order.user:
                raise permissions.PermissionDenied(
                    "You cannot cancel an order you did not place."
                )

        serializer.save()

    def perform_destroy(self, instance):
        # Pushing for Errors: Only allow deletion of 'pending' or 'cancelled' orders.
        if instance.status == "confirmed":
            raise permissions.PermissionDenied(
                "Cannot delete a confirmed order. Please cancel it first if possible."
            )
        instance.delete()
