from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import *
from .models import *


# --- UPDATED: VendorProductViewSet ---
class VendorProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "vendor_profile"):  # Make sure this matches your user model
            return Product.objects.filter(vendor=user.vendor_profile).order_by(
                "-created_at"
            )
        return Product.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, "vendor_profile"):
            serializer.save(vendor=self.request.user.vendor_profile)
        else:
            raise PermissionDenied("You do not have a vendor profile.")

    @action(detail=False, methods=["post"])
    def upload(self, request, *args, **kwargs):
        if not hasattr(request.user, "vendor_profile"):
            return Response(
                {"error": "User is not a vendor."}, status=status.HTTP_403_FORBIDDEN
            )

        # The serializer now expects 'file' and 'image_zip'
        serializer = ProductUploadSerializer(data=request.data)
        if serializer.is_valid():
            num_created = serializer.save(vendor=request.user.vendor_profile)
            return Response(
                {"message": f"Successfully created {num_created} products."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- UPDATED: AdminProductViewSet ---
class AdminProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]  # Best practice to lock this down
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by("-created_at")
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # ... (Your get_queryset logic is fine) ...
        queryset = super().get_queryset()
        vendor_id = self.request.query_params.get("vendor_id")
        if vendor_id:
            queryset = queryset.filter(vendor__id=vendor_id)
        return queryset

    # The single-product create/update methods should work fine with the updated ProductSerializer

    @action(detail=False, methods=["post"], url_path="upload/(?P<vendor_id>[^/.]+)")
    def upload_products(self, request, vendor_id=None, *args, **kwargs):
        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProductUploadSerializer(data=request.data)
        if serializer.is_valid():
            num_created = serializer.save(vendor=vendor)
            return Response(
                {
                    "message": f"Successfully created {num_created} products for vendor {vendor.name}."
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
