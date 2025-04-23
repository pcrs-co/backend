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
        brand= models.CharField(max_length=100, blank=True, null=True)
        model= models.CharField(max_length=100, blank=True, null=True)
        series= models.CharField(max_length=50, blank=True, null=True)
        generation= models.CharField(max_length=50, blank=True, null=True)
        core_count= models.IntegerField( blank=True, null=True)
        thread_count= models.IntegerField( blank=True, null=True)
        base_clock_speed= models.FloatField( blank=True, null=True)
        boost_clock_speed= models.FloatField( blank=True, null=True)
        cache_size= models.CharField(max_length=50, blank=True, null=True)
        integrated_graphics= models.BooleanField(max_length=50, blank=True, null=True) 

    class RAM(models.Model): 
        capacity_gb= models.IntegerField( blank=True, null=True)
        type= models.CharField(max_length=50, blank=True, null=True)
        frequency_mhz= models.IntegerField(blank=True, null=True)
        ecc_support= models.BooleanField( blank=True, null=True)
        channels= models.IntegerField( blank=True, null=True)

    class Storage(models.Model):
        type= models.CharField(max_length=50, blank=True, null=True)
        form_factor= models.CharField(max_length=50, blank=True, null=True)
        capacity_gb= models.IntegerField( blank=True, null=True)
        interface= models.CharField(max_length=50, blank=True, null=True)
        rpm= models.IntegerField(blank=True, null=True)
        read_speed_mbps= models.IntegerField( blank=True, null=True)
        write_speed_mbps= models.IntegerField( blank=True, null=True)

    class Graphic(models.Model):
        gpu_type= models.CharField(max_length=50, blank=True, null=True)
        brand= models.CharField(max_length=50, blank=True, null=True)
        model= models.CharField(max_length=50, blank=True, null=True)
        vram_size_gb= models.IntegerField( blank=True, null=True)
        series= models.CharField(max_length=50, blank=True, null=True)

    class Display(models.Model):
        size_inches= models.FloatField( blank=True, null=True)
        resolution= models.CharField(max_length=50, blank=True, null=True)
        panel_type= models.CharField(max_length=50, blank=True, null=True)
        refresh_rate_hz= models.IntegerField( blank=True, null=True)
        aspect_ratio= models.CharField(max_length=50, blank=True, null=True)

    class PortsConnectivity(models.Model):
        usb_ports= models.IntegerField( blank=True, null=True)
        video_output= models.CharField( blank=True, null=True)
        ethernet_speed= models.FloatField( blank=True, null=True)
        wifi_version= models.CharField(max_length=50, blank=True, null=True)
        bluetooth_version= models.CharField(max_length=50, blank=True, null=True)
        audio_jack= models.BooleanField( blank=True, null=True)
        sd_card_reader= models.BooleanField( blank=True, null=True)

    class PowerBattery(models.Model):
        battery_capacity_wh= models.FloatField( blank=True, null=True)
        adapter_wattage= models.IntegerField( blank=True, null=True)
        estimated_battery_life_hours= models.FloatField( blank=True, null=True)

    class Cooling(models.Model):
        cooling_type= models.CharField(max_length=50, blank=True, null=True)
        fan_count= models.IntegerField( blank=True, null=True)
        cooler_brand= models.CharField(max_length=50, blank=True, null=True)

    class OperatingSystem(models.Model):
        os_name= models.CharField(max_length=50, blank=True, null=True)
        version= models.CharField(max_length=50, blank=True, null=True)
        
    class FormFactor(models.Model):
        type= models.CharField(max_length=50, blank=True, null=True)
        dimensions= models.CharField(max_length=50, blank=True, null=True)
        weight= models.FloatField( blank=True, null=True)

    class Extra(models.Model):
        keyboard_type= models.CharField(max_length=50, blank=True, null=True)
        has_backlit_keyboard= models.BooleanField( blank=True, null=True)
        webcam_resolution= models.CharField(max_length=50, blank=True, null=True)
        biometrics= models.CharField(max_length=50, blank=True, null=True)
        mil_std_certified= models.CharField(max_length=50, blank=True, null=True)

    class Product(models.Model):
        processor = models.ForeignKey('Processor', on_delete=models.CASCADE)
        ram= models.ForeignKey('RAM', on_delete=models.CASCADE)
        storage= models.ForeignKey('Storage', on_delete=models.CASCADE)
        graphic= models.ForeignKey('Graphic', on_delete=models.CASCADE)
        display= models.ForeignKey('Display', on_delete=models.CASCADE)
        ports_connectivity= models.ForeignKey('PortsConnectivity', on_delete=models.CASCADE)
        power_battery= models.ForeignKey('PowerBattery', on_delete=models.CASCADE)
        cooling= models.ForeignKey('Cooling', on_delete=models.CASCADE)
        operating_system= models.ForeignKey('OperatingSystem', on_delete=models.CASCADE)
        form_factor= models.ForeignKey('FormFactor', on_delete=models.CASCADE)
        extra= models.ForeignKey('Extra', on_delete=models.CASCADE)
        vendor= models.ForeignKey('Vendor', on_delete=models.CASCADE)
       
        
    

              
        