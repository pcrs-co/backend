from rest_framework.permissions import AllowAny, IsAuthenticated
from login_and_register.models import CustomUser, Vendor
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import OrderSerializer
from vendor.models import Product
from .models import Order


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate order with logged-in user
            return Response(
                {"message": "Order placed. Awaiting vendor confirmation."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderSerializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Order updated successfully", "order": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return Response(
            {"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )

    # 🔒 Confirm (vendor) / Cancel (user)
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        action = request.data.get("action")

        if action == "cancel":
            if request.user != order.user:
                return Response(
                    {"error": "Only the user who placed this order can cancel it."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            try:
                order.cancel()
                return Response({"message": "Order cancelled."})
            except Exception as e:
                return Response({"error": str(e)}, status=400)

        elif action == "confirm":
            if not hasattr(request.user, "vendor"):
                return Response(
                    {"error": "Only vendors can confirm orders."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if order.vendor and order.vendor.user != request.user:
                return Response(
                    {"error": "You are not the vendor for this order."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            try:
                order.confirm()
                return Response({"message": "Order confirmed."})
            except Exception as e:
                return Response({"error": str(e)}, status=400)

        return Response({"error": "Invalid action."}, status=400)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns a list of orders based on the user's role:
        - Admin/Staff: All orders.
        - Vendor: Orders for their products.
        - Customer: Orders they have placed.
        """
        user = request.user

        if user.is_staff or user.is_superuser:
            # Admin sees all orders
            orders = Order.objects.all().order_by("-created_at")
        elif hasattr(user, "vendor"):
            # Vendor sees orders related to their products
            orders = Order.objects.filter(product__vendor=user.vendor).order_by(
                "-created_at"
            )
        else:
            # Customer sees their own orders
            orders = Order.objects.filter(user=user).order_by("-created_at")

        # We should use a serializer that provides enough context for the frontend
        # (e.g., product name, customer email for the admin/vendor view)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
