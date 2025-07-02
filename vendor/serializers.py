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


# --- UPDATED: ProductSerializer ---
class ProductSerializer(
    serializers.ModelSerializer
):  # No longer needs WritableNestedModelSerializer
    # Nested component serializers for READ operations
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
    # +++ ADD THIS NEW FIELD +++
    vendor_order_summary = serializers.SerializerMethodField()

    # For READ operations, display a list of all associated images
    images = ProductImageSerializer(many=True, read_only=True)

    # For WRITE operations (creating a single product), accept a list of uploaded images
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
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
            "uploaded_images",
            "vendor_order_summary",  # <-- ADD THIS NEW FIELD
        )
        read_only_fields = ("id", "vendor")

    # +++ ADD THIS NEW METHOD +++
    def get_vendor_order_summary(self, obj):
        request = self.context.get("request")
        user = request.user if request else None

        # Check if a user is authenticated and has a vendor profile
        if not (user and user.is_authenticated and hasattr(user, "vendor")):
            return None

        # Check if the authenticated vendor is the one who owns this product
        if user.vendor.id == obj.vendor.id:
            # If so, aggregate order stats for this product
            summary = Order.objects.filter(product=obj).aggregate(
                pending_orders=Count("id", filter=Q(status="pending")),
                confirmed_orders=Count("id", filter=Q(status="confirmed")),
            )
            return summary

        # If the user is a vendor but not the owner, return nothing
        return None

    def _handle_nested_component(self, validated_data, component_name_str, model_class):
        component_data_str = validated_data.pop(component_name_str, "{}")
        try:
            component_data = json.loads(component_data_str)
        except (json.JSONDecodeError, TypeError):
            component_data = {}
        data_received = component_data.get("data_received", "").strip()
        if not data_received:
            return None
        instance, _ = model_class.objects.get_or_create(data_received=data_received)
        return instance

    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop("uploaded_images", [])

        components = {}
        component_map = {
            "processor": Processor,
            "memory": Memory,
            "storage": Storage,
            "graphic": Graphic,
            "display": Display,
            "ports": PortsConnectivity,
            "battery": PowerBattery,
            "cooling": Cooling,
            "operating_system": OperatingSystem,
            "form_factor": FormFactor,
            "extra": Extra,
        }
        for name, model_class in component_map.items():
            components[name] = self._handle_nested_component(
                validated_data, name, model_class
            )

        product = Product.objects.create(**validated_data, **components)

        if images_data:
            for image_file in images_data:
                ProductImage.objects.create(product=product, image=image_file)

        return product

    # Update method would need similar logic, but is more complex to handle image additions/deletions.
    # Focusing on the bulk upload as requested.


# --- FULLY REBUILT: ProductUploadSerializer ---
class ProductUploadSerializer(serializers.Serializer):
    """
    Handles bulk-creating products from a spreadsheet and a single zip file of images.
    This serializer is robust against missing data and uses efficient bulk operations.
    """

    file = serializers.FileField(
        write_only=True, help_text="The spreadsheet (.csv, .xls, .xlsx)."
    )
    image_zip = serializers.FileField(
        write_only=True, required=False, help_text="A zip file containing all images."
    )

    def validate_file(self, value):
        supported_extensions = [".csv", ".xls", ".xlsx"]
        if not any(value.name.lower().endswith(ext) for ext in supported_extensions):
            raise serializers.ValidationError(
                "Unsupported spreadsheet format. Use .csv, .xls, or .xlsx."
            )
        return value

    def validate_image_zip(self, value):
        if value and not value.name.lower().endswith(".zip"):
            raise serializers.ValidationError("Image file must be a .zip archive.")
        return value

    @transaction.atomic
    def save(self, **kwargs):
        vendor = kwargs.get("vendor")
        if not vendor:
            raise serializers.ValidationError(
                "A vendor must be provided to save products."
            )

        spreadsheet_file = self.validated_data["file"]
        zip_file = self.validated_data.get("image_zip")

        # 1. UNZIP IMAGES INTO IN-MEMORY MAP
        image_map = {}
        if zip_file:
            try:
                with zipfile.ZipFile(zip_file, "r") as zf:
                    for filename in zf.namelist():
                        if filename.startswith("__MACOSX/") or filename.endswith("/"):
                            continue

                        image_data = zf.read(filename)
                        in_memory_file = InMemoryUploadedFile(
                            io.BytesIO(image_data),
                            "image",
                            filename,
                            "image/jpeg",
                            len(image_data),
                            None,
                        )
                        base_filename = filename.split("/")[-1]
                        image_map[base_filename] = in_memory_file
            except zipfile.BadZipFile:
                raise serializers.ValidationError(
                    "The uploaded image file is not a valid zip archive."
                )

        # 2. READ SPREADSHEET
        try:
            if spreadsheet_file.name.lower().endswith(".csv"):
                df = pd.read_csv(spreadsheet_file)
            else:
                df = pd.read_excel(spreadsheet_file)

            df = df.astype(str).fillna("")  # Prevents FutureWarning and dtype issues
        except Exception as e:
            raise serializers.ValidationError(f"Could not read the spreadsheet: {e}")

        # 3. SETUP
        component_cache = {}
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

        if "image" not in df.columns:
            df["image"] = ""

        created_count = 0
        images_to_create = []

        # 4. PROCESS EACH ROW AND CREATE PRODUCT & PREPARE IMAGES
        for index, row in df.iterrows():
            try:
                product_components = {}
                for col_name, (model, field_name) in component_map.items():
                    component_name = str(row.get(col_name, "")).strip()
                    if not component_name:
                        continue
                    cache_key = (model, component_name)
                    if cache_key in component_cache:
                        component_instance = component_cache[cache_key]
                    else:
                        component_instance, _ = model.objects.get_or_create(
                            data_received=component_name
                        )
                        component_cache[cache_key] = component_instance
                    product_components[field_name] = component_instance

                price_val = pd.to_numeric(row.get("price"), errors="coerce")
                final_price = (
                    Decimal("0.00") if pd.isna(price_val) else Decimal(price_val)
                )

                # CREATE PRODUCT INDIVIDUALLY TO GUARANTEE IT HAS AN ID
                product_instance = Product.objects.create(
                    name=str(
                        row.get("product_name", f"Unnamed Product {index+1}")
                    ).strip(),
                    price=final_price,
                    brand=str(row.get("brand", "Unknown Brand")).strip(),
                    product_type=str(row.get("product_type", "uncategorized")).strip(),
                    vendor=vendor,
                    **product_components,
                )
                created_count += 1

                # PREPARE IMAGES FOR BULK CREATION LATER
                image_filenames_str = row.get("image", "")
                filenames = [
                    name.strip()
                    for name in image_filenames_str.split(",")
                    if name.strip()
                ]
                for filename in filenames:
                    if filename in image_map:
                        image_file = image_map[filename]
                        images_to_create.append(
                            ProductImage(
                                product_id=product_instance.id,  # Now product_instance.id is guaranteed to exist
                                image=image_file,
                                alt_text=f"{product_instance.name} - {filename}",
                            )
                        )

            except Exception as e:
                print(f"Skipping spreadsheet row {index + 2} due to error: {e}")
                continue

        # 5. BULK CREATE ALL IMAGES AT ONCE
        if images_to_create:
            ProductImage.objects.bulk_create(images_to_create, batch_size=500)

        if created_count == 0:
            raise serializers.ValidationError(
                "No valid product rows were found in the file."
            )

        return created_count


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
