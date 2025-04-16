from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20, unique=True)
    region = models.CharField(max_length=30, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "date_of_birth",
        "region",
    ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Vendor(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="vendor_profile"
    )
    company_name = models.CharField(max_length=255)
    location = models.CharField(
        max_length=255
    )  # can be extended with Google Maps API integration
    verified = models.BooleanField(default=False)  # for admin to verify

    def __str__(self):
        return self.company_name


class Product(models.Model):
    VENDOR_TYPES = [
        ("laptop", "Laptop"),
        ("desktop", "Desktop"),
    ]

    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=50, choices=VENDOR_TYPES)
    brand = models.CharField(max_length=100)
    processor = models.CharField(max_length=100)
    ram = models.CharField(max_length=50)
    storage = models.CharField(max_length=50)
    battery_life = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.product_type} - {self.processor}"
