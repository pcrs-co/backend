from django.db import models
from login_and_register.models import CustomUser, Vendor
from vendor.models import Product


class Order(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name="user",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    vendor = models.ForeignKey(
        Vendor,
        related_name="vendor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        Product,
        related_name="product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
