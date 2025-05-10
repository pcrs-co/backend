from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from .serializers import *
from .models import *


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class VendorManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Vendor registered and email sent."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, vendor_id):
        vendor = get_object_or_404(Vendor, id=vendor_id)
        user = get_object_or_404(CustomUser, id=vendor.user)
        vendor_data = VendorSerializer(vendor).data
        user_data = UserSerializer(vendor.user).data
        combined_data = {"vendor": vendor_data, "user": user_data}
        return Response(combined_data)

    def put(self, request, vendor_id):
        vendor = get_object_or_404(Vendor, id=vendor_id)
        serializer = VendorSerializer(
            vendor, data=request.data, partial=True
        )  # Use partial=True for partial updates
        logo_file = request.FILES.get("logo")

        if serializer.is_valid():
            serializer.save()
            if logo_file:
                logo_obj, created = Vendor.objects.get_or_create(id=user)
                logo_obj.logo = logo_file
                logo_obj.save()
            return Response(
                {"message": "Vendor updated successfully", "vendor": serializer.data}
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, vendor_id):
        vendor = Vendor.objects.get(id=vendor_id)
        user = CustomUser.objects.get(id=vendor.user)
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class UserManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, user_id):
        user = get_object_or_404(Vendor, id=user_id)
        serializer = UserSerializer(
            user, data=request.data, partial=True
        )  # Use partial=True for partial updates
        avatar_file = request.FILES.get("avatar")

        if serializer.is_valid():
            serializer.save()
            if avatar_file:
                avatar_obj, created = Vendor.objects.get_or_create(id=user)
                avatar_obj.logo = avatar_file
                avatar_obj.save()
            return Response(
                {"message": "User updated successfully", "user": serializer.data}
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class VendorListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        vendors = Vendor.objects.all().order_by("id")
        serializer = VendorListSerializer(vendors, many=True)
        return Response(serializer.data)


class UserListView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        avatar_file = request.FILES.get("avatar")

        if serializer.is_valid():
            serializer.save()

            if avatar_file:
                # Update or create avatar
                avatar_obj, created = CustomUser.objects.get_or_create(id=user)
                avatar_obj.avatar = avatar_file
                avatar_obj.save()
            return Response(
                {"message": "User updated successfully", "user": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class VendorView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = VendorSerializer(user, data=request.data, partial=True)
        logo_file = request.FILES.get("logo")

        if serializer.is_valid():
            serializer.save()

            if logo_file:
                logo_obj, created = Vendor.objects.get_or_create(id=user)
                logo_obj.logo = logo_file
                logo_obj.save()
            return Response(
                {"message": "Vendor updated successfully", "vendor": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
