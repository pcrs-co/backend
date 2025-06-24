from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import CustomUser, Vendor
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import status
from .serializers import *

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


# ===================================================================
# 3. ADMIN MANAGEMENT VIEWS (No changes needed here, just confirming)
# ===================================================================


class CustomerManagementViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for managing all CUSTOMER accounts."""

    queryset = CustomUser.objects.filter(groups__name="customer").order_by(
        "-date_joined"
    )
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        # --- THIS IS THE FULLY CORRECTED LOGIC ---

        # For listing multiple customers, use the lightweight list serializer.
        if self.action in ["update", "partial_update"]:
            # For updating, use the specific, limited UpdateUserSerializer.
            return UpdateUserSerializer
        return UserDetailSerializer


class VendorViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for managing all VENDOR accounts."""

    queryset = Vendor.objects.select_related("user").all().order_by("-created_at")
    permission_classes = [IsAdminUser]  # Should be IsAdminUser

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
