from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create a router for ViewSets
router = DefaultRouter()
router.register(r"admin/vendors", VendorViewSet, basename="vendor")
router.register(r"admin/customers", CustomerViewSet, basename="customer")

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="get_token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("register/", UserRegisterView.as_view(), name="register"),
    # User profile endpoints
    path("user/profile/", CustomerProfileView.as_view(), name="customer-profile"),
    path("vendor/profile/", VendorProfileView.as_view(), name="vendor-profile"),
    # Include the router URLs
] + router.urls
