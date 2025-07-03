from rest_framework import serializers
from .models import *

# --- IMPORT NECESSARY SERIALIZERS ---
from login_and_register.serializers import (
    UserDetailSerializer,
    VendorSerializer,
)  # Assuming these exist
from vendor.serializers import ProductSerializer  # Assuming this exists from vendor app


# A minimal serializer for User data within the Order
class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = (
            UserDetailSerializer.Meta.model
        )  # Use the model from UserDetailSerializer
        fields = ["id", "first_name", "last_name", "email", "phone_number"]


# A minimal serializer for Vendor data within the Order
class VendorSimpleSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)  # Nest user details within vendor

    class Meta:
        model = VendorSerializer.Meta.model  # Use the model from VendorSerializer
        fields = [
            "id",
            "company_name",
            "location",
            "user",
        ]  # Include 'user' for phone/email


# A minimal serializer for Product data within the Order
class ProductSimpleSerializer(serializers.ModelSerializer):
    # This just gets the name and price for display in the order list
    class Meta:
        model = ProductSerializer.Meta.model  # Use the model from ProductSerializer
        fields = ["id", "name", "price", "brand"]


class OrderSerializer(serializers.ModelSerializer):
    from login_and_register.serializers import NestedVendorProfileSerializer

    action = serializers.ChoiceField(
        choices=["confirm", "cancel"],
        write_only=True,
        required=False,
        help_text="Send 'confirm' or 'cancel' to change order status.",
    )
    product_name = serializers.StringRelatedField(source="product")

    # --- THIS IS THE FIX: Nest vendor details for the frontend ---
    vendor = NestedVendorProfileSerializer(read_only=True)
    # --- FIX: Use nested serializers for read operations ---
    user = UserSimpleSerializer(read_only=True)
    product = ProductSimpleSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "vendor",
            "product",
            "quantity",
            "product_name",
            "status",
            "created_at",
            "modified_at",
            "action",
        ]
        read_only_fields = [
            "status",
            "user",
            "vendor",
            "created_at",
            "modified_at",
            "product_name",
        ]

    def create(self, validated_data):
        # --- CHANGE START ---
        # FIX: The serializer now delegates the entire creation process to the model manager.
        # This is much cleaner and respects the "Fat Model, Thin Serializer" pattern.
        user = self.context["request"].user
        product = validated_data["product"]
        quantity = validated_data["quantity"]

        try:
            # Call our new, safe creation method.
            order = Order.objects.create_order(
                user=user, product=product, quantity=quantity
            )
            return order
        except ValidationError as e:
            # Pushing for errors: Catch the specific error from the manager and
            # convert it into a DRF-friendly validation error.
            raise serializers.ValidationError({"detail": e.message})
        # --- CHANGE END ---

    def update(self, instance, validated_data):
        # FIX: The update logic is now streamlined to handle actions.
        action = validated_data.get("action")

        # If no action is provided, we assume other fields might be updated (not typical for orders).
        # We will simply pass through to the parent.
        if not action:
            return super().update(instance, validated_data)

        try:
            if action == "confirm":
                instance.confirm()
            elif action == "cancel":
                instance.cancel()
        except Exception as e:
            # Pushing for errors: Catch exceptions from the model and raise a validation error.
            raise serializers.ValidationError({"detail": str(e)})

        return instance


class UserOrderHistorySerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for a user's order history list.
    Includes the product name for easy display.
    """

    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "product_name", "quantity", "status", "created_at"]
