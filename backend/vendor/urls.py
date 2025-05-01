from django.urls import path
from .views import *

urlpatterns = [
    path(
        "vendor/products/<int:vendor_id>/",
        ProductView.as_view(),
        name="vendor-products",
    ),
    path("products/<int:product_id>/", ProductView.as_view(), name="products-view"),
    path(
        "admin/products/<int:product_id>/",
        ProductManagementView.as_view(),
        name="products-view",
    ),
    path("admin/products/", ProductManagementView.as_view(), name="add-products-view"),
    path("product-list/", ProductListView.as_view(), name="product-list"),
]
