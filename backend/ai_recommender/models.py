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


class ApplicationSystemRequirement(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="requirements"
    )
    type = models.CharField(
        max_length=20, choices=[("minimum", "Minimum"), ("recommended", "Recommended")]
    )

    cpu = models.CharField(max_length=255)
    gpu = models.CharField(max_length=255)
    ram = models.IntegerField(help_text="RAM in GB")
    storage = models.IntegerField(help_text="Storage in GB")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)


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
