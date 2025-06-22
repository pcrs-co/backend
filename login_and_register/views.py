from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from .serializers import *
from .models import *


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "per_page"
    max_page_size = 100


# ===================================================================
# 1. AUTHENTICATION & PUBLIC REGISTRATION
# ===================================================================


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view to add user role to the JWT token.
    """

    serializer_class = CustomTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    """
    Public-facing endpoint for a new CUSTOMER to create an account.
    Accessible by anyone.
    """

    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


# ===================================================================
# 2. SELF-SERVICE PROFILE MANAGEMENT (For Logged-in Users)
# ===================================================================


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    """
    Handles GET and PUT/PATCH for the currently authenticated CUSTOMER's profile.
    A user can only see and edit their own data.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        # This securely returns the profile of the user making the request.
        return self.request.user


class VendorProfileView(generics.RetrieveUpdateAPIView):
    """
    Handles GET and PUT/PATCH for the currently authenticated VENDOR's profile.
    A vendor can only see and edit their own data.
    """

    permission_classes = [
        IsAuthenticated
    ]  # You could add a custom IsVendor permission later
    serializer_class = VendorSerializer

    def get_object(self):
        # Securely returns the vendor profile linked to the user making the request.
        # If they are not a vendor, this will correctly return a 404 Not Found.
        return get_object_or_404(Vendor, user=self.request.user)


# ===================================================================
# 3. ADMIN MANAGEMENT VIEWS (For Admins Only)
# ===================================================================


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for managing all CUSTOMER accounts.
    Provides full CRUD functionality over users in the 'customer' group.
    """

    # Query only users in the 'customer' group for this viewset.
    queryset = CustomUser.objects.filter(groups__name="customer").order_by(
        "-date_joined"
    )
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Use a lightweight serializer for the list view for performance.
        if self.action == "list":
            return CustomerListSerializer
        # Use the full serializer for creating, retrieving, or updating.
        return UserSerializer


class VendorViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for managing all VENDOR accounts.
    The admin is the only one who can create new vendors.
    """

    # Use select_related to optimize database queries by fetching the user in the same query.
    queryset = Vendor.objects.select_related("user").all().order_by("-created_at")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return VendorListSerializer
        # For create, retrieve, update, use the full VendorSerializer
        return VendorSerializer

    def create(self, request, *args, **kwargs):
        """
        Custom create method to provide clear error handling.
        """
        serializer = self.get_serializer(data=request.data)
        # is_valid with raise_exception=True will automatically return a 400
        # response with error details if validation fails.
        serializer.is_valid(raise_exception=True)

        # perform_create calls serializer.save(), which in turn calls our
        # custom serializer.create() method.
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method to ensure the associated user is also deleted.
        """
        vendor_profile = self.get_object()
        # Because of the on_delete=models.CASCADE on the OneToOneField,
        # deleting the user will automatically delete the Vendor profile.
        vendor_profile.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
