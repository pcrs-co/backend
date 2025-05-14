from django.db import models
from login_and_register.models import CustomUser, Vendor
from vendor.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

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
    quantity = models.PositiveIntegerField(default=1)  # new field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # only when new
            if self.product.quantity - self.product.pending_quantity < self.quantity:
                raise ValueError("Not enough stock available.")
            self.product.pending_quantity += self.quantity
            self.product.save()
        super().save(*args, **kwargs)

    def confirm(self):
        if self.status == "pending":
            self.product.quantity -= self.quantity
            self.product.pending_quantity -= self.quantity
            self.product.save()
            self.status = "confirmed"
            self.save()

    def cancel(self):
        if self.status == "pending":
            self.product.pending_quantity -= self.quantity
            self.product.save()
            self.status = "cancelled"
            self.save()
