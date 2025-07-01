import difflib
from ai_recommender.models import CPUBenchmark, GPUBenchmark
from login_and_register.models import *
from django.db import models


# +++ REUSABLE HELPER FUNCTION FOR SMART MATCHING +++
def find_best_benchmark_match(target_name: str, benchmark_model):
    """
    Finds the best benchmark record by matching against the correct field ('cpu' or 'gpu')
    and using the performance score as a tie-breaker.

    Args:
        target_name (str): The component name from the product (e.g., "Intel Core i7-13700K").
        benchmark_model: The Django model to search (CPUBenchmark or GPUBenchmark).

    Returns:
        The best matching benchmark object or None.
    """
    if not target_name:
        return None

    all_benchmarks = benchmark_model.objects.all()
    if not all_benchmarks:
        return None

    # --- KEY CHANGE: Determine the correct field name ---
    if benchmark_model == CPUBenchmark:
        name_field = "cpu"
    elif benchmark_model == GPUBenchmark:
        name_field = "gpu"
    else:
        # Safeguard if you add more benchmark types later
        raise TypeError(f"Unsupported benchmark model: {benchmark_model.__name__}")

    best_similarity = 0.0
    best_matches = []

    # Step 1: Find the highest similarity ratio
    for bench in all_benchmarks:
        # Use getattr() to dynamically access the correct field ('cpu' or 'gpu')
        benchmark_name = getattr(bench, name_field)
        similarity = difflib.SequenceMatcher(
            None, target_name.lower(), benchmark_name.lower()
        ).ratio()

        if similarity > best_similarity:
            best_similarity = similarity
            best_matches = [bench]
        elif similarity == best_similarity:
            best_matches.append(bench)

    # Step 2: Avoid matching completely unrelated items
    SIMILARITY_THRESHOLD = 0.7
    if best_similarity < SIMILARITY_THRESHOLD:
        print(
            f"No good match for '{target_name}'. Highest similarity "
            f"({best_similarity:.2f}) is below the {SIMILARITY_THRESHOLD} threshold."
        )
        return None

    # Step 3: From the best matches, pick the one with the highest score as a tie-breaker
    if not best_matches:
        return None

    winner = max(best_matches, key=lambda b: b.score)
    return winner


class Product(models.Model):
    VENDOR_TYPES = [
        ("laptop", "Laptop"),
        ("desktop", "Desktop"),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50, choices=VENDOR_TYPES)
    price = models.DecimalField(max_digits=65, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    pending_quantity = models.PositiveIntegerField(default=0)
    vendor = models.ForeignKey(
        Vendor, related_name="products", on_delete=models.CASCADE
    )
    processor = models.ForeignKey(
        "Processor",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    memory = models.ForeignKey(
        "Memory",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
    ports = models.ForeignKey(
        "PortsConnectivity",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    battery = models.ForeignKey(
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
    # Example addition to Processor and Graphic
    cpu_score = models.IntegerField(blank=True, null=True)
    gpu_score = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    # +++ FINAL, CORRECTED SAVE METHOD +++
    def save(self, *args, **kwargs):
        """
        Overrides the default save method to populate cpu_score and gpu_score.
        This version correctly uses the 'data_received' field from components
        and matches against the specific 'cpu'/'gpu' fields in the benchmark models.
        """
        # --- CPU Score Lookup ---
        # Checks the processor's 'data_received' field, which is set during bulk upload.
        if self.processor and self.processor.data_received:
            best_match = find_best_benchmark_match(
                self.processor.data_received, CPUBenchmark
            )
            if best_match:
                self.cpu_score = best_match.score
                print(
                    f"Success: Matched CPU '{self.processor.data_received}' to benchmark '{best_match.cpu}' (Score: {self.cpu_score})"
                )
            else:
                self.cpu_score = None  # Clear score if no match is found
                print(
                    f"Warning: Could not find a benchmark match for CPU '{self.processor.data_received}'"
                )
        else:
            # If there's no processor or it has no data, score must be null.
            self.cpu_score = None

        # --- GPU Score Lookup ---
        # Repeats the same robust logic for the GPU.
        if self.graphic and self.graphic.data_received:
            best_match = find_best_benchmark_match(
                self.graphic.data_received, GPUBenchmark
            )
            if best_match:
                self.gpu_score = best_match.score
                print(
                    f"Success: Matched GPU '{self.graphic.data_received}' to benchmark '{best_match.gpu}' (Score: {self.gpu_score})"
                )
            else:
                self.gpu_score = None  # Clear score if no match is found
                print(
                    f"Warning: Could not find a benchmark match for GPU '{self.graphic.data_received}'"
                )
        else:
            # If there's no graphic card or it has no data, score must be null.
            self.gpu_score = None

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# --- ADD THIS NEW MODEL ---
def get_product_image_path(instance, filename):
    """Helper function to create a clean upload path for product images."""
    return f"products/{instance.product_id}/{filename}"


class ProductImage(models.Model):
    """
    Stores a single image for a Product. A Product can have many ProductImages.
    """

    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=get_product_image_path)
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="A short description of the image for accessibility.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Processor(models.Model):
    data_received = models.CharField(max_length=1000, null=True, blank=True)
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


class Memory(models.Model):
    data_received = models.CharField(max_length=1000, null=True, blank=True)
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
    data_received = models.CharField(max_length=10000, null=True, blank=True)
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
    data_received = models.CharField(max_length=10000, null=True, blank=True)
    gpu_type = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    vram_size_gb = models.IntegerField(blank=True, null=True)
    series = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class Display(models.Model):
    data_received = models.CharField(max_length=10000, null=True, blank=True)
    size_inches = models.FloatField(blank=True, null=True)
    resolution = models.CharField(max_length=50, blank=True, null=True)
    panel_type = models.CharField(max_length=50, blank=True, null=True)
    refresh_rate_hz = models.IntegerField(blank=True, null=True)
    aspect_ratio = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class PortsConnectivity(models.Model):
    data_received = models.CharField(max_length=10000, null=True, blank=True)
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
    data_received = models.CharField(max_length=10000, null=True, blank=True)
    battery_capacity_wh = models.FloatField(blank=True, null=True)
    adapter_wattage = models.IntegerField(blank=True, null=True)
    estimated_battery_life_hours = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class Cooling(models.Model):
    data_received = models.CharField(max_length=10000, null=True, blank=True)
    cooling_type = models.CharField(max_length=50, blank=True, null=True)
    fan_count = models.IntegerField(blank=True, null=True)
    cooler_brand = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class OperatingSystem(models.Model):
    data_received = models.CharField(max_length=10000, null=True, blank=True)
    os_name = models.CharField(max_length=50, blank=True, null=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class FormFactor(models.Model):
    data_received = models.CharField(max_length=10000, null=True, blank=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    dimensions = models.CharField(max_length=50, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class Extra(models.Model):
    data_received = models.CharField(max_length=10000, null=True, blank=True)
    keyboard_type = models.CharField(max_length=50, blank=True, null=True)
    has_backlit_keyboard = models.BooleanField(blank=True, null=True)
    webcam_resolution = models.CharField(max_length=50, blank=True, null=True)
    biometrics = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
