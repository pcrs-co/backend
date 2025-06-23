from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from rest_framework import serializers
from io import BytesIO
from .models import *
import pandas as pd
import string
import random
import re


class CPUBenchmarkSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="cpu")  # Alias
    benchmark_score = serializers.IntegerField(source="score")  # Alias

    class Meta:
        model = CPUBenchmark
        fields = ["id", "name", "benchmark_score", "cpu_mark", "price"]


class GPUBenchmarkSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="gpu")  # Alias
    benchmark_score = serializers.IntegerField(source="score")

    class Meta:
        model = GPUBenchmark
        fields = ["id", "name", "benchmark_score", "gpu_mark", "price"]


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"


class ApplicationSystemRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSystemRequirement
        fields = "__all__"


class ApplicationSerializer(serializers.ModelSerializer):
    requirements = ApplicationSystemRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = "__all__"


class UserPreferenceSerializer(serializers.ModelSerializer):
    activities = serializers.ListField(child=serializers.CharField(), write_only=True)
    applications = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = UserPreference
        fields = ["activities", "applications", "session_id", "budget"]

    def create(self, validated_data):
        activity_names = validated_data.pop("activities")
        app_names = validated_data.pop("applications")
        preference = UserPreference.objects.create(**validated_data)

        for name in activity_names:
            activity, _ = Activity.objects.get_or_create(
                name__iexact=name.strip(), defaults={"name": name.strip()}
            )
            preference.activities.add(activity)

        for app_name in app_names:
            app = Application.objects.filter(name__iexact=app_name.strip()).first()
            if not app:
                # Fallback: attach to first activity or a dummy
                activity = preference.activities.first() or Activity.objects.first()
                app = Application.objects.create(
                    name=app_name.strip(), activity=activity, intensity_level="medium"
                )
            preference.applications.add(app)

        return preference
