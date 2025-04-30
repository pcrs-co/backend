from django.db import models
from login_and_register.models import *


class Product(models.Model):
    VENDOR_TYPES = [
        ("laptop", "Laptop"),
        ("desktop", "Desktop"),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50, choices=VENDOR_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vendor = models.ForeignKey(
        CustomUser, related_name="products", on_delete=models.CASCADE
    )
    processor = models.ForeignKey(
        "Processor",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ram = models.ForeignKey(
        "RAM", related_name="products", on_delete=models.SET_NULL, null=True, blank=True
    )
    storage = models.ForeignKey(
        "Storage",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    graphic = models.ForeignKey(
        "Graphic",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    display = models.ForeignKey(
        "Display",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ports_connectivity = models.ForeignKey(
        "PortsConnectivity",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    power_battery = models.ForeignKey(
        "PowerBattery",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cooling = models.ForeignKey(
        "Cooling",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    operating_system = models.ForeignKey(
        "OperatingSystem",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    form_factor = models.ForeignKey(
        "FormFactor",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    extra = models.ForeignKey(
        "Extra",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Processor(models.Model):
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    series = models.CharField(max_length=50, blank=True, null=True)
    generation = models.CharField(max_length=50, blank=True, null=True)
    core_count = models.IntegerField(blank=True, null=True)
    thread_count = models.IntegerField(blank=True, null=True)
    base_clock_speed = models.FloatField(blank=True, null=True)
    boost_clock_speed = models.FloatField(blank=True, null=True)
    cache_size = models.CharField(max_length=50, blank=True, null=True)
    integrated_graphics = models.BooleanField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class RAM(models.Model):
    capacity_gb = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    frequency_mhz = models.IntegerField(blank=True, null=True)
    ecc_support = models.BooleanField(blank=True, null=True)
    channels = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "capacity_gb",
            "type",
            "frequency_mhz",
            "ecc_support",
            "channels",
        )


class Storage(models.Model):
    type = models.CharField(max_length=50, blank=True, null=True)
    form_factor = models.CharField(max_length=50, blank=True, null=True)
    capacity_gb = models.IntegerField(blank=True, null=True)
    interface = models.CharField(max_length=50, blank=True, null=True)
    rpm = models.IntegerField(blank=True, null=True)
    read_speed_mbps = models.IntegerField(blank=True, null=True)
    write_speed_mbps = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class Graphic(models.Model):
    gpu_type = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    vram_size_gb = models.IntegerField(blank=True, null=True)
    series = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class Display(models.Model):
    size_inches = models.FloatField(blank=True, null=True)
    resolution = models.CharField(max_length=50, blank=True, null=True)
    panel_type = models.CharField(max_length=50, blank=True, null=True)
    refresh_rate_hz = models.IntegerField(blank=True, null=True)
    aspect_ratio = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class PortsConnectivity(models.Model):
    usb_ports = models.IntegerField(blank=True, null=True)
    video_output = models.CharField(max_length=100, blank=True, null=True)
    ethernet_speed = models.FloatField(blank=True, null=True)
    wifi_version = models.CharField(max_length=50, blank=True, null=True)
    bluetooth_version = models.CharField(max_length=50, blank=True, null=True)
    audio_jack = models.BooleanField(blank=True, null=True)
    sd_card_reader = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class PowerBattery(models.Model):
    battery_capacity_wh = models.FloatField(blank=True, null=True)
    adapter_wattage = models.IntegerField(blank=True, null=True)
    estimated_battery_life_hours = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class Cooling(models.Model):
    cooling_type = models.CharField(max_length=50, blank=True, null=True)
    fan_count = models.IntegerField(blank=True, null=True)
    cooler_brand = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class OperatingSystem(models.Model):
    os_name = models.CharField(max_length=50, blank=True, null=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class FormFactor(models.Model):
    type = models.CharField(max_length=50, blank=True, null=True)
    dimensions = models.CharField(max_length=50, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class Extra(models.Model):
    keyboard_type = models.CharField(max_length=50, blank=True, null=True)
    has_backlit_keyboard = models.BooleanField(blank=True, null=True)
    webcam_resolution = models.CharField(max_length=50, blank=True, null=True)
    biometrics = models.CharField(max_length=50, blank=True, null=True)
    mil_std_certified = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
