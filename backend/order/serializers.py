from rest_framework import serializers
from .models import *


class OrderSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = ["status", "created_at", "modified_at"]

    def create(self, validated_data):
        product = validated_data["product"]
        quantity = validated_data["quantity"]

        # Check if enough stock is available (considering pending orders)
        if product.quantity - product.pending_quantity < quantity:
            raise serializers.ValidationError("Not enough stock available.")

        # Reserve stock as pending
        product.pending_quantity += quantity
        product.save()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get("status", old_status)

        if old_status != "confirmed" and new_status == "confirmed":
            product = instance.product
            quantity_requested = instance.quantity

            if product.quantity < quantity_requested:
                raise serializers.ValidationError(
                    "Not enough stock to confirm this order."
                )

            # Now we actually reduce stock
            product.quantity -= quantity_requested
            product.save()

        return super().update(instance, validated_data)


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def update(self, instance, validated_data):
        new_status = validated_data.get("status")
        if instance.status != "pending":
            raise serializers.ValidationError("Only pending orders can be updated.")

        if new_status == "confirmed":
            instance.confirm()
        elif new_status == "cancelled":
            instance.cancel()
        else:
            raise serializers.ValidationError("Invalid status transition.")
        return instance
