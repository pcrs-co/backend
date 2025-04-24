from django.urls import path
from .views import *

urlpatterns = [
    path("products/<int:vendor_id>/", ProductView.as_view(), name="products"),
]
