from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework import status, viewsets
from .serializers import *
from .models import *


class VendorProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    # The global paginator will be applied automatically to the list view.

    def get_queryset(self):
        """This view should only return products for the currently authenticated vendor."""
        user = self.request.user
        if hasattr(user, "vendor"):
            return Product.objects.filter(vendor=user.vendor).order_by("-created_at")
        return Product.objects.none()

    def perform_create(self, serializer):
        """Automatically associate the new product with the logged-in vendor."""
        if hasattr(self.request.user, "vendor"):
            serializer.save(vendor=self.request.user.vendor)
        else:
            raise PermissionDenied(
                "You do not have a vendor profile to create products."
            )

    @action(detail=False, methods=["post"], url_path="upload")
    def upload_products(self, request, *args, **kwargs):
        """Handles product file upload for the authenticated vendor."""
        user = self.request.user
        if not hasattr(user, "vendor"):
            return Response(
                {"error": "User is not a vendor."}, status=status.HTTP_403_FORBIDDEN
            )

        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProductUploadSerializer(data={"file": file})
        serializer.is_valid(raise_exception=True)
        serializer.save(vendor=user.vendor)
        return Response(
            {"message": "Products uploaded successfully"},
            status=status.HTTP_201_CREATED,
        )


class AdminProductViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated
    ]  # Should be [IsAdminUser] for better security
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by("-created_at")
    # The global paginator will be applied automatically.

    def get_queryset(self):
        """
        Admins can filter products by a specific vendor using a query parameter.
        e.g., /api/admin/products/?vendor_id=123
        """
        queryset = super().get_queryset()
        vendor_id = self.request.query_params.get("vendor_id")
        if vendor_id:
            # Use __id for clarity, though just 'vendor' works too
            queryset = queryset.filter(vendor__id=vendor_id)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        vendor_id = data.get("vendor")

        try:
            vendor = (
                Vendor.objects.get(id=vendor_id)
                if vendor_id
                else request.user.vendor_profile
            )
            data["vendor"] = vendor.id
        except (Vendor.DoesNotExist, AttributeError):
            return Response(
                {"error": "Vendor not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(
            {"message": "Product created successfully", "product": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        vendor_id = data.get("vendor")

        if vendor_id:
            try:
                vendor = Vendor.objects.get(id=vendor_id)
                data["vendor"] = vendor.id
            except Vendor.DoesNotExist:
                return Response(
                    {"error": "Vendor not found"}, status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(
            {"message": "Product updated successfully", "product": serializer.data}
        )

    @action(detail=False, methods=["post"], url_path="upload/(?P<vendor_id>[^/.]+)")
    def upload_products(self, request, vendor_id=None):
        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]
        serializer = ProductUploadSerializer(data={"file": file})

        if serializer.is_valid():
            serializer.save(vendor_id=vendor.id)
            return Response(
                {
                    "message": "Products uploaded successfully",
                    "count": (
                        serializer.instance.count()
                        if hasattr(serializer, "instance")
                        else 0
                    ),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"error": "Upload failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
