from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

# The router will correctly generate:
# /api/vendor/products/
# /api/vendor/products/upload/
# /api/admin/products/
# /api/admin/products/upload/

router.register(r"vendor/products", VendorProductViewSet, basename="vendor-product")
router.register(r"admin/products", AdminProductViewSet, basename="admin-product")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "products/<int:id>/",
        PublicProductDetailView.as_view(),
        name="public-product-detail",
    ),
    path("products/", PublicProductListView.as_view(), name="public-product-list"),
]
