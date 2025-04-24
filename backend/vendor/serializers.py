from django.contrib.auth.password_validation import validate_password
from login_and_register.models import *
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from rest_framework import serializers
from io import BytesIO
from .models import *
import pandas as pd
import string
import random
import re


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith((".csv", ".xls", ".xlsx", ".ods")):
            raise serializers.ValidationError(
                "Unsupported file format. Please upload a CSV, Excel, or ODS file."
            )
        return value

    def save(self, vendor_id):
        file = self.validated_data["file"]

        # Handle the file based on its extension
        if file.name.endswith(".csv"):
            df = pd.read_csv(file, encoding="utf-8")
        elif file.name.endswith((".xls", ".xlsx", ".ods")):
            df = pd.read_excel(
                file, engine="odf" if file.name.endswith(".ods") else None
            )

        vendor = Vendor.objects.get(id=vendor_id)  # Get the vendor

        # Process each row in the file and create/update models accordingly
        for _, row in df.iterrows():
            processor, _ = Processor.objects.get_or_create(
                name=row["processor"],
                model=row["processor_model"],
            )

            ram, _ = RAM.objects.get_or_create(
                capacity_gb=row["ram_capacity"],
                type=row["ram_type"],
                frequency_mhz=row["ram_frequency"],
            )

            # Continue for other fields like Storage, Graphic, etc.
            storage, _ = Storage.objects.get_or_create(
                capacity_gb=row["storage_capacity"],
                type=row["storage_type"],
            )

            # Create the Product and link specs
            product = Product.objects.create(
                name=row["product_name"],
                price=row["price"],
                processor=processor,
                ram=ram,
                storage=storage,
                vendor=vendor,
            )
            product.save()
