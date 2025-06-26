from login_and_register.models import *
from django.db.models import Q
from django.db import models
import uuid


class Activity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class Application(models.Model):
    name = models.CharField(max_length=255)
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name="applications"
    )
    intensity_level = models.CharField(
        max_length=10, choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")]
    )
    source = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CPUBenchmark(models.Model):
    cpu = models.CharField(max_length=255, unique=True)
    score = models.IntegerField()
    rank = models.IntegerField(null=True, blank=True)
    value_score = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.cpu} (Score: {self.score})"


class GPUBenchmark(models.Model):
    gpu = models.CharField(max_length=255, unique=True)
    score = models.IntegerField()
    rank = models.IntegerField(null=True, blank=True)
    value_score = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.gpu} (Score: {self.score})"


class DiskBenchmark(models.Model):
    drive_name = models.CharField(max_length=255, unique=True)
    size_tb = models.FloatField(null=True, blank=True)
    score = models.IntegerField()
    rank = models.IntegerField(null=True, blank=True)
    value_score = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.drive_name} (Score: {self.score})"


class ApplicationSystemRequirement(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="requirements"
    )
    type = models.CharField(
        max_length=20, choices=[("minimum", "Minimum"), ("recommended", "Recommended")]
    )

    cpu = models.CharField(max_length=255)
    gpu = models.CharField(max_length=255)
    cpu_score = models.IntegerField()
    gpu_score = models.IntegerField()
    ram = models.IntegerField(help_text="RAM in GB")

    # -- MODIFIED STORAGE --
    storage_size = models.IntegerField(
        help_text="Storage in GB"
    )  # Renamed from 'storage'
    storage_type = models.CharField(
        max_length=10,
        choices=[("SSD", "SSD"), ("HDD", "HDD"), ("Any", "Any")],
        default="Any",
    )  # ++ ADDED ++
    storage_score = models.IntegerField(
        null=True, blank=True, help_text="Target score from DiskBenchmark"
    )  # ++ ADDED ++
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.cpu and not self.cpu_score:
            cpu_bench = (
                CPUBenchmark.objects.filter(cpu__iexact=self.cpu)
                .order_by("-score")
                .first()
            )
            if cpu_bench:
                self.cpu_score = cpu_bench.score

        if self.gpu and self.gpu_score is None:
            # -- FIXED: Removed non-existent field `gpu_mark` from query --
            gpu_bench = (
                GPUBenchmark.objects.filter(gpu__iexact=self.gpu)
                .order_by("-score")
                .first()
            )
            if gpu_bench:
                self.gpu_score = gpu_bench.score

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application.name} ({self.type})"


class UserPreference(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    activities = models.ManyToManyField(Activity)
    applications = models.ManyToManyField(Application, blank=True)
    budget = models.DecimalField(max_digits=65, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class RecommendationSpecification(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    session_id = models.CharField(
        max_length=255, null=True, blank=True
    )  # if not logged in
    type = models.CharField(
        max_length=20,
        choices=[("recommended", "Recommended"), ("minimum", "Minimum")],
        default="recommended",
    )
    source_preference = models.ForeignKey(
        UserPreference, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # -- RECOMMENDED (standardized names) --
    recommended_cpu_name = models.CharField(max_length=255, null=True, blank=True)
    recommended_gpu_name = models.CharField(max_length=255, null=True, blank=True)
    recommended_cpu_score = models.IntegerField(null=True, blank=True)
    recommended_gpu_score = models.IntegerField(null=True, blank=True)
    recommended_ram = models.IntegerField(null=True, blank=True)
    recommended_storage_size = models.IntegerField(null=True, blank=True)  # ++ RENAMED
    recommended_storage_type = models.CharField(
        max_length=10, default="Any"
    )  # ++ ADDED

    # -- MINIMUM (standardized names) --
    min_cpu_name = models.CharField(max_length=255, null=True, blank=True)
    min_gpu_name = models.CharField(max_length=255, null=True, blank=True)
    min_cpu_score = models.IntegerField(null=True, blank=True)
    min_gpu_score = models.IntegerField(null=True, blank=True)
    min_ram = models.IntegerField(null=True, blank=True)
    min_storage_size = models.IntegerField(null=True, blank=True)  # ++ RENAMED
    min_storage_type = models.CharField(max_length=10, default="Any")  # ++ ADDED

    def __str__(self):
        user_or_session = self.user.email if self.user else f"Session {self.session_id}"
        return f"Recommendation for {user_or_session} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class SystemRequirementExtraction(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    source_url = models.URLField()
    raw_text = models.TextField()  # unstructured scraped text
    extracted_cpu = models.CharField(max_length=255, blank=True)
    extracted_gpu = models.CharField(max_length=255, blank=True)
    extracted_ram = models.IntegerField(null=True, blank=True)
    extracted_storage = models.IntegerField(null=True, blank=True)
    extraction_method = models.CharField(max_length=100, default="rule-based")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class RequirementMatch(models.Model):
    extraction = models.ForeignKey(
        SystemRequirementExtraction, on_delete=models.CASCADE
    )
    matched_cpu = models.ForeignKey(
        CPUBenchmark, null=True, blank=True, on_delete=models.SET_NULL
    )
    matched_gpu = models.ForeignKey(
        GPUBenchmark, null=True, blank=True, on_delete=models.SET_NULL
    )
    cpu_confidence = models.FloatField(default=0.0)
    gpu_confidence = models.FloatField(default=0.0)
    match_method = models.CharField(max_length=100, default="exact")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class AdminCorrectionLog(models.Model):
    match = models.ForeignKey(RequirementMatch, on_delete=models.CASCADE)
    corrected_cpu = models.ForeignKey(
        CPUBenchmark,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="corrected_cpu",
    )
    corrected_gpu = models.ForeignKey(
        GPUBenchmark,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="corrected_gpu",
    )
    reason = models.TextField(blank=True)
    corrected_by = models.ForeignKey(
        CustomUser, null=True, blank=True, on_delete=models.SET_NULL
    )
    corrected_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class RequirementExtractionLog(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    source_text = models.TextField()
    extracted_json = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, default="regex")
    confidence = models.FloatField(null=True)
    reviewed = models.BooleanField(default=False)


class ApplicationExtractionLog(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    source_text = models.TextField()
    extracted_apps = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50)
    confidence = models.FloatField()
    reviewed = models.BooleanField(default=False)


class ScrapingLog(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    source = models.CharField(max_length=50)
    app_count = models.PositiveIntegerField()
    timestamp = models.DateTimeField()
