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


class ProductSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        # Extract nested spec data
        processor_data = validated_data.pop("processor")
        ram_data = validated_data.pop("ram")
        storage_data = validated_data.pop("storage")
        graphic_data = validated_data.pop("graphic")
        display_data = validated_data.pop("display")
        ports_data = validated_data.pop("ports")
        battery_data = validated_data.pop("battery")
        cooling_data = validated_data.pop("cooling")
        os_data = validated_data.pop("operating_system")
        form_data = validated_data.pop("form_factor")
        extra_data = validated_data.pop("extra")

        # Create nested objects
        processor = Processor.objects.create(**processor_data)
        memory = Memory.objects.create(**ram_data)
        storage = Storage.objects.create(**storage_data)
        graphic = Graphic.objects.create(**graphic_data)
        display = Display.objects.create(**display_data)
        ports = PortsConnectivity.objects.create(**ports_data)
        battery = PowerBattery.objects.create(**battery_data)
        cooling = Cooling.objects.create(**cooling_data)
        os = OperatingSystem.objects.create(**os_data)
        form = FormFactor.objects.create(**form_data)
        extra = Extra.objects.create(**extra_data)

        # Create the product
        product = Product.objects.create(
            processor=processor,
            memory=memory,
            storage=storage,
            graphic=graphic,
            display=display,
            ports=ports,
            battery=battery,
            cooling=cooling,
            operating_system=os,
            form_factor=form,
            extra=extra,
            **validated_data,
        )

        return product

    # In vendor/serializers.py, inside ProductSerializer

    def update(self, instance, validated_data):
        # A mapping of field names to their data and instance objects
        nested_fields = {
            "processor": (validated_data.pop("processor", None), instance.processor),
            "memory": (validated_data.pop("memory", None), instance.memory),
            "storage": (validated_data.pop("storage", None), instance.storage),
            "graphic": (validated_data.pop("graphic", None), instance.graphic),
            "display": (validated_data.pop("display", None), instance.display),
            "ports": (validated_data.pop("ports", None), instance.ports),
            "battery": (validated_data.pop("battery", None), instance.battery),
            # ... add all other nested fields here
        }

        # Loop through the nested fields and update them dynamically
        for field_name, (data, nested_instance) in nested_fields.items():
            if data and nested_instance:
                for attr, value in data.items():
                    setattr(nested_instance, attr, value)
                nested_instance.save()

        # Update the main Product fields
        # This part remains the same
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


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

        # Read the file
        if file.name.endswith(".csv"):
            df = pd.read_csv(file, encoding="utf-8")
        elif file.name.endswith((".xls", ".xlsx", ".ods")):
            df = pd.read_excel(
                file, engine="odf" if file.name.endswith(".ods") else None
            )

        # Normalize missing values
        df.fillna("", inplace=True)

        # Fetch vendor
        vendor = Vendor.objects.get(id=vendor_id)

        for index, row in df.iterrows():
            try:
                processor, _ = Processor.objects.get_or_create(
                    data_received=row.get("processor", "")
                )
                memory, _ = Memory.objects.get_or_create(
                    data_received=row.get("memory", "")
                )
                storage, _ = Storage.objects.get_or_create(
                    data_received=row.get("storage", "")
                )
                graphic, _ = Graphic.objects.get_or_create(
                    data_received=row.get("graphic", "")
                )
                display, _ = Display.objects.get_or_create(
                    data_received=row.get("display", "")
                )
                ports, _ = PortsConnectivity.objects.get_or_create(
                    data_received=row.get("ports", "")
                )
                battery, _ = PowerBattery.objects.get_or_create(
                    data_received=row.get("battery", "")
                )
                cooling, _ = Cooling.objects.get_or_create(
                    data_received=row.get("cooling", "")
                )
                operating_system, _ = OperatingSystem.objects.get_or_create(
                    data_received=row.get("os", "")
                )
                form_factor, _ = FormFactor.objects.get_or_create(
                    data_received=row.get("formfactor", "")
                )
                extra, _ = Extra.objects.get_or_create(
                    data_received=row.get("extra", "")
                )

                # Create product
                product = Product.objects.create(
                    name=row.get("product_name", ""),
                    price=row.get("price", 0),
                    brand=row.get("brand", ""),
                    product_type=row.get("product_type", ""),
                    processor=processor,
                    memory=memory,
                    storage=storage,
                    graphic=graphic,
                    display=display,
                    ports=ports,
                    battery=battery,
                    cooling=cooling,
                    operating_system=operating_system,
                    form_factor=form_factor,
                    extra=extra,
                    vendor=vendor,
                )
                product.save()

            except Exception as e:
                # Log the error
                print(f"Failed to process row {index}: {e}")
                continue


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
