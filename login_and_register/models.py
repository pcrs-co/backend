from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True)
    region = models.CharField(max_length=30, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to="user_avatar/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone_number",
        "email",
    ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Vendor(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="vendor_profile"
    )
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="vendor_logos/", null=True, blank=True)
    location = models.CharField(
        max_length=255
    )  # can be extended with Google Maps API integration
    verified = models.BooleanField(default=False)  # for admin to verify
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
