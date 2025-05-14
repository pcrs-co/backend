from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status, viewsets
from .serializers import *
from .models import *


class VendorProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                self.get_serializer(product).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(self.get_serializer(product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="upload/(?P<vendor_id>[^/.]+)")
    def upload_products(self, request, vendor_id=None):
        """
        Custom route: /products/upload/<vendor_id>/
        Accepts a file and bulk uploads products for a vendor.
        """
        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]
        serializer = ProductUploadSerializer(data={"file": file})

        if serializer.is_valid():
            serializer.save(vendor_id=vendor_id)
            return Response(
                {"message": "Products uploaded successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        vendor_id = self.request.query_params.get("vendor_id")
        if vendor_id:
            return self.queryset.filter(vendor__id=vendor_id)
        return self.queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        vendor_id = data.get("vendor")
        if vendor_id:
            try:
                vendor = Vendor.objects.get(id=vendor_id)
                data["vendor"] = vendor.id
            except vendor.DoesNotExist:
                return Response(
                    {"error": "Vendor not found."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Optional: set admin as vendor if no vendor is given
            data["vendor"] = request.user.id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                self.get_serializer(product).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        # Optional: Allow changing vendor
        vendor_id = data.get("vendor")
        if vendor_id:
            try:
                vendor = User.objects.get(id=vendor_id)
                data["vendor"] = vendor.id
            except User.DoesNotExist:
                return Response(
                    {"error": "Vendor not found."}, status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(instance, data=data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(self.get_serializer(product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="upload/(?P<vendor_id>[^/.]+)")
    def upload_products(self, request, vendor_id=None):
        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vendor = User.objects.get(id=vendor_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Vendor not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]
        serializer = ProductUploadSerializer(data={"file": file})

        if serializer.is_valid():
            serializer.save(vendor_id=vendor.id)
            return Response(
                {"message": "Products uploaded successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
