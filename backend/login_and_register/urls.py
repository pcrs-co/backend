from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
from django.urls import path

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="get_token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("admin/user_list/", UserListView.as_view(), name="user_list"),
    path("admin/register/user", UserManagementView.as_view(), name="add_user"),
    path("admin/users/<int:user_id>", UserManagementView.as_view(), name="crud_user"),
    path("admin/vendor/", VendorManagementView.as_view(), name="register_vendor"),
    path(
        "admin/vendor/<int:vendor_id>",
        VendorManagementView.as_view(),
        name="crud_vendor",
    ),
    path("user/", UserView.as_view(), name="user"),
    path("vendor/", VendorView.as_view(), name="user"),
]
