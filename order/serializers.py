from rest_framework import serializers
from .models import *


class OrderSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(
        choices=["confirm", "cancel"],
        write_only=True,
        required=False,
        help_text="Send 'confirm' or 'cancel' to change order status.",
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "vendor",
            "product",
            "quantity",
            "status",
            "created_at",
            "modified_at",
            "action",
        ]
        read_only_fields = ["status", "user", "vendor", "created_at", "modified_at"]

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
