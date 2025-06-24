from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create a router for ViewSets
router = DefaultRouter()
router.register(r"admin/vendors", VendorViewSet, basename="vendor")
router.register(r"admin/customers", CustomerManagementViewSet, basename="customer")

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="get_token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("register/", UserRegisterView.as_view(), name="register"),
    # User profile endpoints
    # Self-service Profile URL - This is the one your frontend will hit
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    # Include the router URLs
] + router.urls
