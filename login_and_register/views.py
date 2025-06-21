from rest_framework.permissions import AllowAny, IsAuthenticated
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


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all().order_by("created_at")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return VendorListSerializer
        return VendorSerializer

    def retrieve(self, request, *args, **kwargs):
        vendor = self.get_object()
        vendor_data = VendorSerializer(vendor).data
        user_data = UserSerializer(vendor.user).data
        combined_data = {"vendor": vendor_data, "user": user_data}
        return Response(combined_data)
    
    # --- ADD THIS METHOD ---
    def create(self, request, *args, **kwargs):
        # Use the correct serializer for creation
        serializer = self.get_serializer(data=request.data)
        
        # This is the most important part.
        # If validation fails, it stops here and returns a 400 response.
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            # You can log the validation error here if you want
            # print(f"Validation Error: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # If validation passes, then we proceed to save.
        # Any error inside the serializer's .create() method will now
        # be caught as a 500 error, which is correct.
        try:
            vendor = serializer.save()
        except Exception as e:
            # Catch any other unexpected errors during creation
            # print(f"Unexpected Error during vendor creation: {e}")
            return Response(
                {"detail": "An internal error occurred during vendor creation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # If everything succeeds, return the 201 Created response.
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    # --- END OF ADDED METHOD ---


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        vendor = self.get_object()
        serializer = VendorSerializer(vendor, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            logo_file = request.FILES.get("logo")
            if logo_file:
                vendor.logo = logo_file
                vendor.save()
            return Response(
                {"message": "Vendor updated successfully", "vendor": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        vendor = self.get_object()
        user = vendor.user
        vendor.delete()
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(groups__name="default").order_by("created_at")
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return CustomerListSerializer  # Only lightweight fields for list view
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        customer = self.get_object()
        serializer = UserSerializer(customer, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            avatar_file = request.FILES.get("avatar")
            if avatar_file:
                customer.avatar = avatar_file
                customer.save()
            return Response(
                {"message": "Updated successfully", "customer": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
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
        request.user.delete()
        return Response({"message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)


class VendorProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get the Vendor instance linked to the current user
        vendor = get_object_or_404(Vendor, user=request.user)
        vendor_data = VendorSerializer(vendor).data
        user_data = UserSerializer(vendor.user).data
        combined_data = {"vendor": vendor_data, "user": user_data}
        return Response(combined_data)

    def put(self, request):
        vendor = get_object_or_404(Vendor, user=request.user)
        serializer = VendorSerializer(vendor, data=request.data, partial=True)
        logo_file = request.FILES.get("logo")

        if serializer.is_valid():
            serializer.save()
            if logo_file:
                vendor.logo = logo_file
                vendor.save()
            return Response(
                {"message": "Vendor updated successfully", "vendor": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
