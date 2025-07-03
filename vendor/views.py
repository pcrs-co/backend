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


class VendorProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "vendor"):
            return Product.objects.filter(vendor=user.vendor).order_by("-created_at")
        return Product.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, "vendor"):
            serializer.save(vendor=self.request.user.vendor)
        else:
            raise PermissionDenied("You do not have a vendor profile.")

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request, *args, **kwargs):
        user = self.request.user
        if not hasattr(user, "vendor"):
            return Response(
                {"error": "You do not have a vendor profile to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ProductUploadSerializer(data=request.data)
        if serializer.is_valid():
            num_created = serializer.save(vendor=user.vendor)
            return Response(
                {"message": f"Successfully created {num_created} products."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by("-created_at")
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        vendor_id = self.request.query_params.get("vendor_id")
        if vendor_id:
            queryset = queryset.filter(vendor__id=vendor_id)
        return queryset

    # --- FIX: Standardize the custom action ---
    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request, *args, **kwargs):
        # We will get the vendor_id from the form data, not the URL.
        vendor_id = request.data.get("vendor_id")
        if not vendor_id:
            return Response(
                {"error": "vendor_id is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        # We pass the full request data to the serializer
        serializer = ProductUploadSerializer(data=request.data)
        if serializer.is_valid():
            num_created = serializer.save(vendor=vendor)
            return Response(
                {
                    "message": f"Successfully created {num_created} products for vendor {vendor.company_name}."
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# +++ ADD THIS NEW VIEW AT THE END OF THE FILE +++
class PublicProductDetailView(generics.RetrieveAPIView):
    """
    A public endpoint to view the full details of a single product.
    It uses the main ProductSerializer, which will conditionally add
    vendor-specific data if the requester is the owner.
    """

    queryset = (
        Product.objects.select_related(
            "vendor",
            "processor",
            "memory",
            "storage",
            "graphic",
            "display",
            "ports",
            "battery",
            "cooling",
            "operating_system",
            "form_factor",
            "extra",
        )
        .prefetch_related("images")
        .all()
    )
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"  # The URL will use the product ID


# --- ADD THIS NEW VIEW AT THE END OF THE FILE ---
class PublicProductListView(generics.ListAPIView):
    """
    A public, read-only endpoint that lists all available products.
    """

    queryset = Product.objects.all().order_by("-created_at")
    # We use the standard ProductSerializer for public viewing
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
