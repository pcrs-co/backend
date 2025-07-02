from drf_writable_nested.serializers import WritableNestedModelSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.files.uploadedfile import InMemoryUploadedFile
from login_and_register.serializers import VendorSerializer
from order.models import Order  # <--- ADD THIS IMPORT
from django.contrib.auth.models import Group
from login_and_register.models import *
from rest_framework import serializers
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.db import transaction
from decimal import Decimal
from io import BytesIO
from .models import *
import pandas as pd
import zipfile
import string
import random
import json
import re
import io


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


# --- NEW SERIALIZER FOR NESTING ---
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text"]


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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text"]


# --- THE MAIN SERIALIZER for a SINGLE PRODUCT ---
class ProductSerializer(serializers.ModelSerializer):
    # For READ operations, use the detailed component serializers.
    processor = ProcessorSerializer(read_only=True)
    memory = MemorySerializer(read_only=True)
    storage = StorageSerializer(read_only=True)
    graphic = GraphicSerializer(read_only=True)
    display = DisplaySerializer(read_only=True)
    ports = PortsConnectivitySerializer(read_only=True)
    battery = PowerBatterySerializer(read_only=True)
    cooling = CoolingSerializer(read_only=True)
    operating_system = OperatingSystemSerializer(read_only=True)
    form_factor = FormFactorSerializer(read_only=True)
    extra = ExtraSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    # This is a computed field for the vendor dashboard.
    vendor_order_summary = serializers.SerializerMethodField()

    # For WRITE operations (creating/updating a single product), accept raw text.
    processor_str = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    memory_str = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    storage_str = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    graphic_str = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    # ... Add more _str fields for other components if needed ...

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(use_url=False), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "brand",
            "price",
            "quantity",
            "product_type",
            "vendor",
            "processor",
            "memory",
            "storage",
            "graphic",
            "display",
            "ports",
            "battery",
            "cooling",
            "operating_system",
            "form_factor",
            "extra",
            "images",
            "vendor_order_summary",
            # Write-only fields
            "processor_str",
            "memory_str",
            "storage_str",
            "graphic_str",
            "uploaded_images",
        )
        read_only_fields = ("id", "vendor")

    def _get_or_create_component(self, data_received, ModelClass):
        if not data_received or not data_received.strip():
            return None
        # This one line handles everything: finding an existing component or creating a new one.
        # When a new one is created, its .save() method is called, which triggers the score lookup.
        instance, _ = ModelClass.objects.get_or_create(
            data_received=data_received.strip()
        )
        return instance

    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop("uploaded_images", [])

        # Create/get components from the raw string data
        product_components = {
            "processor": self._get_or_create_component(
                validated_data.pop("processor_str", ""), Processor
            ),
            "memory": self._get_or_create_component(
                validated_data.pop("memory_str", ""), Memory
            ),
            "storage": self._get_or_create_component(
                validated_data.pop("storage_str", ""), Storage
            ),
            "graphic": self._get_or_create_component(
                validated_data.pop("graphic_str", ""), Graphic
            ),
            "display": validated_data.pop("display", None),
            "ports": validated_data.pop("ports", None),
            "battery": validated_data.pop("battery", None),
            "cooling": validated_data.pop("cooling", None),
            "operating_system": validated_data.pop("operating_system", None),
            "form_factor": validated_data.pop("form_factor", None),
            "extra": validated_data.pop("extra", None),
            # ... handle other components ...
        }

        # Create the product with the linked components
        product = Product.objects.create(**validated_data, **product_components)

        # Create associated images
        if images_data:
            ProductImage.objects.bulk_create(
                [
                    ProductImage(product=product, image=image_file)
                    for image_file in images_data
                ]
            )
        return product

    def get_vendor_order_summary(self, obj):
        # This logic is correct and does not need changes.
        request = self.context.get("request")
        user = request.user if request else None
        if not (
            user
            and user.is_authenticated
            and hasattr(user, "vendor")
            and user.vendor.id == obj.vendor.id
        ):
            return None
        return Order.objects.filter(product=obj).aggregate(
            pending_orders=Count("id", filter=Q(status="pending")),
            confirmed_orders=Count("id", filter=Q(status="confirmed")),
        )


# --- THE MAIN SERIALIZER for BULK UPLOADS ---
class ProductUploadSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)
    image_zip = serializers.FileField(write_only=True, required=False)

    def validate_file(self, value):
        if not any(
            value.name.lower().endswith(ext) for ext in [".csv", ".xls", ".xlsx"]
        ):
            raise serializers.ValidationError(
                "Unsupported file format. Use .csv, .xls, or .xlsx."
            )
        return value

    @transaction.atomic
    def save(self, **kwargs):
        vendor = kwargs.get("vendor")
        spreadsheet_file = self.validated_data["file"]
        zip_file = self.validated_data.get("image_zip")

        # 1. Unzip Images into an in-memory map
        image_map = {}
        if zip_file:
            try:
                with zipfile.ZipFile(zip_file, "r") as zf:
                    for filename in zf.namelist():
                        if filename.startswith("__MACOSX/") or filename.endswith("/"):
                            continue
                        base_filename = filename.split("/")[-1]
                        image_data = zf.read(filename)
                        image_map[base_filename] = InMemoryUploadedFile(
                            io.BytesIO(image_data),
                            "image",
                            base_filename,
                            "image/jpeg",
                            len(image_data),
                            None,
                        )
            except zipfile.BadZipFile:
                raise serializers.ValidationError(
                    "The uploaded image file is not a valid zip archive."
                )

        # 2. Read Spreadsheet
        try:
            df = (
                pd.read_excel(spreadsheet_file)
                if spreadsheet_file.name.lower().endswith((".xls", ".xlsx"))
                else pd.read_csv(spreadsheet_file)
            )
            df = df.astype(str).replace("nan", "").fillna("")
        except Exception as e:
            raise serializers.ValidationError(f"Could not read the spreadsheet: {e}")

        # 3. Process Rows
        component_cache = {}
        component_map = {
            "processor": Processor,
            "memory": Memory,
            "storage": Storage,
            "graphic": Graphic,
        }

        products_to_create = []
        image_links_to_create = []

        for index, row in df.iterrows():
            product_components = {}
            for col_name, ModelClass in component_map.items():
                component_text = str(row.get(col_name, "")).strip()
                if not component_text:
                    continue

                if (ModelClass, component_text) not in component_cache:
                    instance, _ = ModelClass.objects.get_or_create(
                        data_received=component_text
                    )
                    component_cache[(ModelClass, component_text)] = instance
                product_components[col_name] = component_cache[
                    (ModelClass, component_text)
                ]

            product_instance = Product(
                name=str(row.get("name", f"Product {index+1}")).strip(),
                brand=str(row.get("brand", "N/A")).strip(),
                product_type=str(row.get("product_type", "laptop")).strip(),
                price=Decimal(row.get("price", "0.00")),
                quantity=int(row.get("quantity", 1)),
                vendor=vendor,
                **product_components,
            )
            products_to_create.append(product_instance)

            image_filenames = [
                name.strip()
                for name in str(row.get("image", "")).split(",")
                if name.strip()
            ]
            image_links_to_create.append(image_filenames)

        # 4. Bulk Create Products & Images
        created_products = Product.objects.bulk_create(products_to_create)

        images_to_create = []
        for product, filenames in zip(created_products, image_links_to_create):
            for filename in filenames:
                if filename in image_map:
                    images_to_create.append(
                        ProductImage(product=product, image=image_map[filename])
                    )

        if images_to_create:
            ProductImage.objects.bulk_create(images_to_create)

        return len(created_products)


class ProductRecommendationSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    processor = ProcessorSerializer(read_only=True)
    memory = MemorySerializer(read_only=True)
    storage = StorageSerializer(read_only=True)
    graphic = GraphicSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    # --- The New Field to Explain the Match ---
    match_details = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "product_type",
            "price",
            "vendor",
            "processor",
            "memory",
            "storage",
            "graphic",
            "images",
            "match_details",  # <-- Add the new field
        ]

    def get_match_details(self, obj):
        # Retrieve the recommendation spec from the context we passed in the view
        rec_spec = self.context.get("rec_spec")
        spec_level = self.context.get("spec_level")
        if not rec_spec:
            return None

        # Determine which spec level to compare against
        if spec_level == "minimum":
            target_cpu_score = rec_spec.min_cpu_score or 0
            target_gpu_score = rec_spec.min_gpu_score or 0
            target_ram = rec_spec.min_ram or 0
        else:
            target_cpu_score = rec_spec.recommended_cpu_score or 0
            target_gpu_score = rec_spec.recommended_gpu_score or 0
            target_ram = rec_spec.recommended_ram or 0

        # Get the product's actual specs
        product_cpu_score = obj.cpu_score or 0
        product_gpu_score = obj.gpu_score or 0
        product_ram = obj.memory.capacity_gb if obj.memory else 0

        # --- Logic to generate helpful tags ---
        tags = []
        is_perfect_match = (
            product_cpu_score >= target_cpu_score
            and product_gpu_score >= target_gpu_score
            and product_ram >= target_ram
        )

        if is_perfect_match:
            tags.append({"text": "Perfect Match", "type": "success"})

        # Add tags for exceeding specs
        if product_cpu_score > target_cpu_score * 1.2:  # Exceeds by 20%
            tags.append({"text": "Better CPU", "type": "info"})
        if product_gpu_score > target_gpu_score * 1.2:
            tags.append({"text": "Better GPU", "type": "info"})

        # Add tags for missing specs (only if not a perfect match)
        if not is_perfect_match:
            if product_cpu_score < target_cpu_score:
                tags.append({"text": "Weaker CPU", "type": "warning"})
            if product_gpu_score < target_gpu_score:
                tags.append({"text": "Weaker GPU", "type": "warning"})
            if product_ram < target_ram:
                tags.append({"text": "Less RAM", "type": "warning"})

        return {
            "match_score": getattr(
                obj, "match_score", 0
            ),  # Get the score we annotated in the view
            "tags": tags,
        }
