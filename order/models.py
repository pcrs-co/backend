from login_and_register.models import CustomUser, Vendor
from django.core.exceptions import ValidationError
from django.db import models, transaction
from vendor.models import Product


class OrderManager(models.Manager):
    """Custom manager for the Order model to encapsulate creation logic."""

    def create_order(self, user, product, quantity):
        """
        Creates a new order after validating stock and creating a pending reservation.
        This is the single, authoritative method for creating an order.
        """
        if product.quantity - product.pending_quantity < quantity:
            # Pushing for errors: Raise a specific, clear error.
            raise ValidationError("Not enough stock available to place this order.")

        with transaction.atomic():
            # Reserve stock as pending.
            product.pending_quantity += quantity
            product.save(update_fields=["pending_quantity"])

            # Create the order object.
            order = self.create(
                user=user,
                product=product,
                vendor=product.vendor,  # Vendor is derived from the product.
                quantity=quantity,
            )
            return order


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

    def confirm(self):
        """Confirms an order, moving stock from pending to sold. Pushes for errors."""
        if self.status != "pending":
            raise ValidationError("Only pending orders can be confirmed.")

        with transaction.atomic():
            # Lock the product row to prevent race conditions during confirmation.
            product = Product.objects.select_for_update().get(id=self.product.id)

            # Check if there's enough stock to fulfill the order *now*.
            if product.quantity < self.quantity:
                raise ValidationError(
                    f"Not enough stock for {product.name} to confirm order."
                )

            # Decrement actual stock AND the pending reservation.
            product.quantity -= self.quantity
            product.pending_quantity -= self.quantity
            product.save()

            self.status = "confirmed"
            self.save(update_fields=["status", "modified_at"])

    def cancel(self):
        """Cancels a pending order, releasing the reserved stock. Pushes for errors."""
        if self.status != "pending":
            raise ValidationError("Only pending orders can be cancelled.")

        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=self.product.id)
            # Release the pending quantity.
            product.pending_quantity -= self.quantity
            product.save()

            self.status = "cancelled"
            self.save(update_fields=["status", "modified_at"])
