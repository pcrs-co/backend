from drf_writable_nested.serializers import WritableNestedModelSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.files.uploadedfile import InMemoryUploadedFile
from login_and_register.serializers import VendorSerializer
from django.contrib.auth.models import Group
from login_and_register.models import *
from rest_framework import serializers
from django.core.mail import send_mail
from django.db import transaction
from io import BytesIO
from .models import *
import pandas as pd
import zipfile
import string
import random
import json
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
        )
        read_only_fields = ("id", "vendor")

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
    file = serializers.FileField(
        write_only=True, help_text="The spreadsheet (.csv, .xls, .xlsx)."
    )
    image_zip = serializers.FileField(
        write_only=True, required=False, help_text="A zip file containing all images."
    )

    def validate_file(self, value):
        supported_extensions = [".csv", ".xls", ".xlsx"]
        if not any(value.name.lower().endswith(ext) for ext in supported_extensions):
            raise serializers.ValidationError("Unsupported spreadsheet format.")
        return value

    def validate_image_zip(self, value):
        if value and not value.name.lower().endswith(".zip"):
            raise serializers.ValidationError("Image file must be a .zip archive.")
        return value

    @transaction.atomic
    def save(self, **kwargs):
        vendor = kwargs["vendor"]
        spreadsheet_file = self.validated_data["file"]
        zip_file = self.validated_data.get("image_zip")

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

        try:
            df = (
                pd.read_excel(spreadsheet_file)
                if not spreadsheet_file.name.lower().endswith(".csv")
                else pd.read_csv(spreadsheet_file)
            )
            df.fillna("", inplace=True)
        except Exception as e:
            raise serializers.ValidationError(f"Could not read the spreadsheet: {e}")

        products_to_create = []
        product_image_relations = {}
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
            "os": (OperatingSystem, "os"),
            "formfactor": (FormFactor, "form_factor"),
            "extra": (Extra, "extra"),
        }

        if "image" not in df.columns:
            df["image"] = ""
        df["image"] = df["image"].astype(str)

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

                product_instance = Product(
                    name=row.get("product_name", f"Unnamed Product {index+1}"),
                    price=pd.to_numeric(row.get("price"), errors="coerce") or 0.0,
                    brand=row.get("brand", "Unknown Brand"),
                    product_type=row.get("product_type", "uncategorized"),
                    vendor=vendor,
                    **product_components,
                )
                products_to_create.append(product_instance)

                image_filenames_str = row.get("image", "")
                if image_filenames_str:
                    filenames = [
                        name.strip() for name in image_filenames_str.split(",")
                    ]
                    product_image_relations[product_instance] = filenames
            except Exception as e:
                print(f"Skipping row {index + 2} due to error: {e}")
                continue

        if not products_to_create:
            raise serializers.ValidationError(
                "No valid product rows found in the file."
            )

        created_products = Product.objects.bulk_create(
            products_to_create, batch_size=500
        )

        images_to_create = []
        for i, product_instance in enumerate(products_to_create):
            db_product = created_products[i]
            if product_instance in product_image_relations:
                filenames = product_image_relations[product_instance]
                for filename in filenames:
                    if filename in image_map:
                        image_file = image_map[filename]
                        images_to_create.append(
                            ProductImage(
                                product=db_product,
                                image=image_file,
                                alt_text=f"{db_product.name} - {filename}",
                            )
                        )
        if images_to_create:
            ProductImage.objects.bulk_create(images_to_create, batch_size=500)

        return len(created_products)


# --- UPDATED: ProductRecommendationSerializer ---
class ProductRecommendationSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    processor = ProcessorSerializer(read_only=True)
    memory = MemorySerializer(read_only=True)
    storage = StorageSerializer(read_only=True)
    graphic = GraphicSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)  # <-- ADD THIS

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
            "images",  # <-- ADD images
        ]
