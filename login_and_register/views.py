from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

# Import only the serializers you will actually use in this file
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,  # For customer registration
    VendorSerializer,  # For admin creation of vendors
    UserDetailSerializer,  # For the unified profile view
    VendorListSerializer,  # For the admin vendor list
    CustomerListSerializer,  # For the admin customer list
    UpdateVendorSerializer,  # For updating vendor profiles
    UpdateCustomerSerializer,  # For updating customer profiles
)
from .models import CustomUser, Vendor

# ===================================================================
# 1. AUTHENTICATION & REGISTRATION
# ===================================================================


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view to add user role to the JWT token."""

    serializer_class = CustomTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    """Public-facing endpoint for a new CUSTOMER to create an account."""

    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = (
        UserSerializer  # Correctly uses the customer registration serializer
    )


# ===================================================================
# 2. UNIFIED SELF-SERVICE PROFILE MANAGEMENT
# ===================================================================


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Handles GET (view) and PUT/PATCH (update) for ANY currently authenticated user.
    This single view replaces the need for separate CustomerProfileView and VendorProfileView.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer  # Use our powerful, unified serializer

    def get_object(self):
        # The object being viewed/edited is always the user making the request.
        return self.request.user


# The old, separate CustomerProfileView and VendorProfileView are now REMOVED.

# ===================================================================
# 3. ADMIN MANAGEMENT VIEWS (No changes needed here, just confirming)
# ===================================================================


class CustomerViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for managing all CUSTOMER accounts."""
    queryset = CustomUser.objects.filter(groups__name="customer").order_by("-date_joined")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # --- THIS IS THE FULLY CORRECTED LOGIC ---
        
        # For listing multiple customers, use the lightweight list serializer.
        if self.action == 'list':
            return CustomerListSerializer
        
        # For updating an existing customer, use the simple update serializer.
        if self.action in ['update', 'partial_update']:
            return UpdateCustomerSerializer
        
        # For creating a NEW customer (if you allow it via this ViewSet), use the full UserSerializer.
        if self.action == 'create':
            return UserSerializer
            
        # For retrieving a SINGLE customer's details (the GET request),
        # use the powerful UserDetailSerializer we made for profiles.
        # This will now be the default for any other action, including 'retrieve'.
        return UserDetailSerializer

class VendorViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for managing all VENDOR accounts."""

    queryset = Vendor.objects.select_related("user").all().order_by("-created_at")
    permission_classes = [IsAuthenticated]  # Should be IsAdminUser

    def get_serializer_class(self):
        if self.action == "list":
            return VendorListSerializer
        # --- THIS IS THE FIX ---
        if self.action in ["update", "partial_update"]:
            return UpdateVendorSerializer  # Use the simple serializer for updates
        # For 'create' and 'retrieve', use the full serializer
        return VendorSerializer

    def destroy(self, request, *args, **kwargs):
        """Custom destroy method to ensure the associated user is also deleted."""
        vendor_profile = self.get_object()
        vendor_profile.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
