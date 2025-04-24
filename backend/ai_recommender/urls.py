from django.urls import path
from .views import *

urlpatterns = [
    path("user_preference", UserPreferenceView.as_view(), name="user_preference"),
]
