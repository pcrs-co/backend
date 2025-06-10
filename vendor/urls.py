from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorProductViewSet, AdminProductViewSet

router = DefaultRouter()

# Register admin and vendor routes with unique prefixes
router.register(r"admin/products", AdminProductViewSet, basename="products")
router.register(r"vendor/products", VendorProductViewSet, basename="vendor_product")

urlpatterns = [
    path("", include(router.urls)),
]
