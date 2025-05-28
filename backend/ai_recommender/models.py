from login_and_register.models import *
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


class CPUBenchmark(models.Model):
    cpu = models.CharField(max_length=255)  # "Intel Core i7-9700K"
    cpu_mark = models.CharField(max_length=255)
    score = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=65)


class GPUBenchmark(models.Model):
    cpu = models.CharField(max_length=255)  # "NVIDIA RTX 3070"
    cpu_mark = models.CharField(max_length=255)
    score = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=65)


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
    storage = models.IntegerField(help_text="Storage in GB")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.cpu and not self.cpu_score:
            cpu_bench = CPUBenchmark.objects.filter(cpu__icontains=self.cpu).order_by('-score').first()
            if cpu_bench:
                self.cpu_score = cpu_bench.score

        if self.gpu and not self.gpu_score:
            gpu_bench = GPUBenchmark.objects.filter(cpu__icontains=self.gpu).order_by('-score').first()
            if gpu_bench:
                self.gpu_score = gpu_bench.score

        super().save(*args, **kwargs)


class UserPreference(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    activities = models.ManyToManyField(Activity)
    custom_applications = models.TextField(blank=True, null=True)
    profession = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


class Question(models.Model):
    QUESTION_TYPES = [
        ("choice", "Multiple Choice"),
        ("text", "Text Input"),
        ("boolean", "Yes/No"),
        ("scale", "Scale (1-5)"),
    ]
    slug = models.SlugField(unique=True)  # like "battery_life"
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    options = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text


class UserAnswer(models.Model):
    preference = models.ForeignKey(
        "UserPreference", on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question.slug}: {self.answer}"


class RecommendationSpecification(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    session_id = models.CharField(
        max_length=255, null=True, blank=True
    )  # if not logged in
    created_at = models.DateTimeField(auto_now_add=True)

    min_cpu_score = models.FloatField()
    min_gpu_score = models.FloatField()
    min_ram = models.IntegerField()
    min_storage = models.IntegerField()

    def __str__(self):
        return f"Recommendation for {self.user or self.session_id} at {self.created_at}"
