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


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class CPUBenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPUBenchmark
        fields = "__all__"


class GPUBenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPUBenchmark
        fields = "__all__"


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

    class Meta:
        model = UserPreference
        fields = ["activities", "custom_applications", "profession", "session_id"]

    def create(self, validated_data):
        activity_names = validated_data.pop("activities")
        preference = UserPreference.objects.create(**validated_data)
        for name in activity_names:
            activity, _ = Activity.objects.get_or_create(
                name__iexact=name.strip(), defaults={"name": name.strip()}
            )
            preference.activities.add(activity)
        return preference


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = "__all__"


class RecommendationInputSerializer(serializers.Serializer):
    profession = serializers.CharField()
    primary_activities = serializers.ListField(child=serializers.CharField())
    technical_level = serializers.ChoiceField(choices=["technical", "non-technical"])
    budget = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

class RecommendationSpecificationDetailedSerializer(serializers.ModelSerializer):
    cpu_details = serializers.SerializerMethodField()
    gpu_details = serializers.SerializerMethodField()

    class Meta:
        model = RecommendationSpecification
        fields = [
            "id",
            "created_at",
            "min_ram",
            "min_storage",
            "cpu_details",
            "gpu_details",
        ]

    def get_cpu_details(self, obj):
        cpu = CPUBenchmark.objects.filter(score__gte=obj.min_cpu_score).order_by("score").first()
        if cpu:
            return {
                "name": cpu.cpu,
                "score": cpu.score,
                "price": str(cpu.price),
            }
        return None

    def get_gpu_details(self, obj):
        gpu = GPUBenchmark.objects.filter(score__gte=obj.min_gpu_score).order_by("score").first()
        if gpu:
            return {
                "name": gpu.cpu,  # It's still named 'cpu' in your GPU model
                "score": gpu.score,
                "price": str(gpu.price),
            }
        return None