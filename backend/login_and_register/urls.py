from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
from django.urls import path

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="get_token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("register/vendor", VendorRegisterView.as_view(), name="register_vendor"),
    path("user/", UserView.as_view(), name="user"),
    path("products/<int:vendor_id>/", ProductView.as_view(), name="products"),
]
