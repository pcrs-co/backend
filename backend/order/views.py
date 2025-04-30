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
            serializer.save()
            return Response(
                {"message": "Preparing to Notify Vendor"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderSerializer(order, id=order_id)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Order updated successfully", "order": serializer.data}
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def delete(self, request, order_id):
        order = Order.objects.get(id=order_id)
        order.delete()
        return Response(
            {"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class OrderListView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
