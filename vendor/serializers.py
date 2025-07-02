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
from decimal import Decimal, InvalidOperation
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


# --- FULLY REBUILT AND CORRECTED: ProductUploadSerializer ---
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

    def _clean_price(self, price_str):
        """A robust helper to clean and convert a price string to a Decimal."""
        if price_str is None or pd.isna(price_str):
            return Decimal("0.00")

        # Convert to string and remove anything that is not a digit or a decimal point.
        cleaned_str = re.sub(r"[^0-9.]", "", str(price_str))

        if not cleaned_str:
            return Decimal("0.00")

        try:
            return Decimal(cleaned_str)
        except InvalidOperation:
            # If conversion fails after cleaning, return 0.00
            return Decimal("0.00")

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

        # 1. UNZIP IMAGES
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
            df = (
                pd.read_excel(spreadsheet_file)
                if spreadsheet_file.name.lower().endswith((".xls", ".xlsx"))
                else pd.read_csv(spreadsheet_file)
            )
            df = df.astype(str).replace("nan", "").fillna("")
        except Exception as e:
            raise serializers.ValidationError(f"Could not read the spreadsheet: {e}")

        # 3. SETUP
        component_cache, created_count, images_to_create = {}, 0, []
        component_map = {
            "processor": Processor,
            "memory": Memory,
            "storage": Storage,
            "graphic": Graphic,
            "display": Display,
            "ports": PortsConnectivity,
            "battery": PowerBattery,
            "cooling": Cooling,
            "os": OperatingSystem,
            "formfactor": FormFactor,
            "extra": Extra,
        }

        if "image" not in df.columns:
            df["image"] = ""

        # 4. PROCESS EACH ROW
        for index, row in df.iterrows():
            try:
                product_components = {}
                for col_name, model_class in component_map.items():
                    data_str = str(row.get(col_name, "")).strip()
                    if not data_str:
                        continue
                    cache_key = (model_class, data_str)
                    if cache_key not in component_cache:
                        instance, _ = model_class.objects.get_or_create(
                            data_received=data_str
                        )
                        component_cache[cache_key] = instance
                    product_components[col_name] = component_cache[cache_key]

                # --- THIS IS THE FIX ---
                # Use the robust cleaning helper function
                final_price = self._clean_price(row.get("price"))

                # Create product individually to get an ID for images
                product_instance = Product.objects.create(
                    name=str(
                        row.get("product_name", f"Unnamed Product {index+1}")
                    ).strip(),
                    price=final_price,
                    brand=str(row.get("brand", "Unknown Brand")).strip(),
                    product_type=str(row.get("product_type", "laptop")).strip().lower(),
                    vendor=vendor,
                    **product_components,
                )
                created_count += 1

                # Prepare images for this product
                filenames = [
                    name.strip()
                    for name in str(row.get("image", "")).split(",")
                    if name.strip()
                ]
                for filename in filenames:
                    if filename in image_map:
                        images_to_create.append(
                            ProductImage(
                                product=product_instance,
                                image=image_map[filename],
                                alt_text=f"{product_instance.name}",
                            )
                        )
            except Exception as e:
                print(f"Skipping spreadsheet row {index + 2} due to error: {e}")
                continue

        # 5. BULK CREATE IMAGES
        if images_to_create:
            ProductImage.objects.bulk_create(images_to_create, batch_size=100)

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
