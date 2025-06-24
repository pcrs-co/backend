from drf_writable_nested.serializers import WritableNestedModelSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from login_and_register.serializers import VendorSerializer
from login_and_register.models import *
from django.core.mail import send_mail
from rest_framework import serializers
from django.db import transaction
from io import BytesIO
from .models import *
import pandas as pd
import string
import random
import re


class ProcessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processor
        fields = "__all__"


class MemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Memory
        fields = "__all__"


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = "__all__"


class GraphicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graphic
        fields = "__all__"


class DisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Display
        fields = "__all__"


class PortsConnectivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PortsConnectivity
        fields = "__all__"


class PowerBatterySerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerBattery
        fields = "__all__"


class CoolingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooling
        fields = "__all__"


class OperatingSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatingSystem
        fields = "__all__"


class FormFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFactor
        fields = "__all__"


class ExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra
        fields = "__all__"


class ProductSerializer(WritableNestedModelSerializer):
    processor = ProcessorSerializer()
    memory = MemorySerializer()
    storage = StorageSerializer()
    graphic = GraphicSerializer()
    display = DisplaySerializer()
    ports = PortsConnectivitySerializer()
    battery = PowerBatterySerializer()
    cooling = CoolingSerializer()
    operating_system = OperatingSystemSerializer()
    form_factor = FormFactorSerializer()
    extra = ExtraSerializer()

    class Meta:
        model = Product
        fields = "__all__"


class ProductUploadSerializer(serializers.Serializer):
    """
    Handles the validation and processing of an uploaded spreadsheet (CSV, Excel)
    to bulk-create products for a specific vendor.

    This serializer is designed for performance by using in-memory caching for
    component lookups and a single bulk_create query for all new products.
    """

    file = serializers.FileField(write_only=True)

    def validate_file(self, value):
        """
        Ensures the uploaded file is of a supported spreadsheet format.
        """
        # Pushing for errors: Be strict about supported file types.
        supported_extensions = [".csv", ".xls", ".xlsx"]
        if not any(value.name.lower().endswith(ext) for ext in supported_extensions):
            raise serializers.ValidationError(
                "Unsupported file format. Please upload a CSV or Excel file (.xls, .xlsx)."
            )
        return value

    @transaction.atomic
    def save(self, vendor):
        """
        Processes the validated file to create products in bulk.

        Args:
            vendor (Vendor): The vendor instance to which the new products will be associated.

        Returns:
            int: The number of products successfully created.
        """
        file = self.validated_data["file"]

        # --- 1. READ FILE INTO PANDAS DATAFRAME ---
        try:
            if file.name.lower().endswith(".csv"):
                df = pd.read_csv(file, encoding="utf-8")
            else:
                df = pd.read_excel(file)
            # Standardize missing data to empty strings for consistency
            df.fillna("", inplace=True)
        except Exception as e:
            # Pushing for errors: Handle file reading errors gracefully.
            raise serializers.ValidationError(f"Could not read the file: {e}")

        # --- 2. PREPARE FOR BULK PROCESSING ---
        products_to_create = []

        # In-memory cache to avoid repeated database hits for the same component
        # within a single file upload. E.g., if 20 laptops have the same "Intel Core i7" CPU.
        component_cache = {}

        # Map spreadsheet column names to their corresponding model and field.
        # This makes the loop below cleaner and easier to maintain.
        component_map = {
            "processor": (Processor, "processor"),
            "memory": (Memory, "memory"),
            "storage": (Storage, "storage"),
            "graphic": (Graphic, "graphic"),
            "display": (Display, "display"),
            "ports": (PortsConnectivity, "ports"),
            "battery": (PowerBattery, "battery"),
            "cooling": (Cooling, "cooling"),
            "os": (OperatingSystem, "operating_system"),
            "formfactor": (FormFactor, "form_factor"),
            "extra": (Extra, "extra"),
        }

        # --- 3. PROCESS EACH ROW IN MEMORY ---
        for index, row in df.iterrows():
            try:
                product_components = {}

                # Loop through our component map to get/create each component instance.
                for col_name, (model, field_name) in component_map.items():
                    component_name = str(row.get(col_name, "")).strip()
                    cache_key = (model, component_name)

                    if cache_key in component_cache:
                        # Use the cached object if we've seen this component before.
                        component_instance = component_cache[cache_key]
                    else:
                        # If not cached, hit the database once and then cache the result.
                        component_instance, _ = model.objects.get_or_create(
                            data_received=component_name
                        )
                        component_cache[cache_key] = component_instance

                    product_components[field_name] = component_instance

                # Instantiate the Product object in memory without saving it to the DB yet.
                product_instance = Product(
                    name=row.get("product_name", "Unnamed Product"),
                    price=pd.to_numeric(row.get("price"), errors="coerce") or 0.0,
                    brand=row.get("brand", "Unknown Brand"),
                    product_type=row.get("product_type", "uncategorized"),
                    vendor=vendor,
                    **product_components,  # Unpack all the component instances
                )
                products_to_create.append(product_instance)

            except Exception as e:
                # Pushing for errors: Log bad rows but continue processing the rest of the file.
                print(f"Skipping row {index + 2} due to error: {e}")
                continue

        # --- 4. EXECUTE BULK CREATE QUERY ---
        if not products_to_create:
            # Pushing for errors: If no valid products were processed, inform the user.
            raise serializers.ValidationError(
                "No valid product rows found in the uploaded file."
            )

        try:
            # Create all the prepared product objects in a single, efficient database query.
            # `batch_size` helps manage memory for extremely large files (10,000+ rows).
            created_products = Product.objects.bulk_create(
                products_to_create, batch_size=500
            )
            return len(created_products)
        except Exception as e:
            # Pushing for errors: Catch potential database-level errors during the bulk insert.
            raise serializers.ValidationError(
                f"A database error occurred during bulk creation: {e}"
            )


class ProductRecommendationSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer()
    processor = ProcessorSerializer()
    memory = MemorySerializer()
    storage = StorageSerializer()
    graphic = GraphicSerializer()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "product_type",
            "price",
            "cpu_score",
            "gpu_score",
            "vendor",
            "processor",
            "memory",
            "storage",
            "graphic",
        ]
