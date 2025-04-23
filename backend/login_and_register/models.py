from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20, unique=True)
    region = models.CharField(max_length=30, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to="user_avatar/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "date_of_birth",
        "region",
    ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Vendor(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="vendor_profile"
    )
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="vendor_logos/", null=True, blank=True)
    location = models.CharField(
        max_length=255
    )  # can be extended with Google Maps API integration
    verified = models.BooleanField(default=False)  # for admin to verify
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name


class Processor(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    series = models.CharField(max_length=50)
    generation = models.CharField(max_length=50)
    core_count = models.IntegerField()
    thread_count = models.IntegerField()
    base_clock_speed = models.FloatField()
    boost_clock_speed = models.FloatField()
    cache_size = models.CharField(max_length=50)
    integrated_graphics = models.BooleanField(max_length=50)

    class RAM(models.Model):
        capacity_gb = models.IntegerField()
        type = models.CharField(max_length=50)
        frequency_mhz = models.IntegerField()
        ecc_support = models.BooleanField()
        channels = models.IntegerField()

    class Storage(models.Model):
        type = models.CharField(max_length=50)
        form_factor = models.CharField(max_length=50)
        capacity_gb = models.IntegerField()
        interface = models.CharField(max_length=50)
        rpm = models.IntegerField()
        read_speed_mbps = models.IntegerField()
        write_speed_mbps = models.IntegerField()

    class Graphic(models.Model):
        gpu_type = models.CharField(max_length=50)
        brand = models.CharField(max_length=50)
        model = models.CharField(max_length=50)
        vram_size_gb = models.IntegerField()
        series = models.CharField(max_length=50)

    class Display(models.Model):
        size_inches = models.FloatField()
        resolution = models.CharField(max_length=50)
        panel_type = models.CharField(max_length=50)
        refresh_rate_hz = models.IntegerField()
        aspect_ratio = models.CharField(max_length=50)

    class PortsConnectivity(models.Model):
        usb_ports = models.IntegerField()
        video_output = models.CharField()
        ethernet_speed = models.FloatField()
        wifi_version = models.CharField(max_length=50)
        bluetooth_version = models.CharField(max_length=50)
        audio_jack = models.BooleanField()
        sd_card_reader = models.BooleanField()

    class PowerBattery(models.Model):
        battery_capacity_wh = models.FloatField()
        adapter_wattage = models.IntegerField()
        estimated_battery_life_hours = models.FloatField()

    class Cooling(models.Model):
        cooling_type = models.CharField(max_length=50)
        fan_count = models.IntegerField()
        cooler_brand = models.CharField(max_length=50)

    class OperatingSystem(models.Model):
        os_name = models.CharField(max_length=50)
        version = models.CharField(max_length=50)

    class FormFactor(models.Model):
        type = models.CharField(max_length=50)
        dimensions = models.CharField(max_length=50)
        weight = models.FloatField()

    class Extra(models.Model):
        keyboard_type = models.CharField(max_length=50)
        has_backlit_keyboard = models.BooleanField()
        webcam_resolution = models.CharField(max_length=50)
        biometrics = models.CharField(max_length=50)
        mil_std_certified = models.CharField(max_length=50)

    class Product(models.Model):
        processor = models.ForeignKey(Processor, on_delete=models.CASCADE)
        ram = models.ForeignKey(RAM, on_delete=models.CASCADE)
        storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
        graphic = models.ForeignKey(Graphic, on_delete=models.CASCADE)
        display = models.ForeignKey(Display, on_delete=models.CASCADE)
        ports_connectivity = models.ForeignKey(
            PortsConnectivity, on_delete=models.CASCADE
        )
        power_battery = models.ForeignKey(PowerBattery, on_delete=models.CASCADE)
        cooling = models.ForeignKey(Cooling, on_delete=models.CASCADE)
        operating_system = models.ForeignKey(OperatingSystem, on_delete=models.CASCADE)
        form_factor = models.ForeignKey(FormFactor, on_delete=models.CASCADE)
        extra = models.ForeignKey(Extra, on_delete=models.CASCADE)
