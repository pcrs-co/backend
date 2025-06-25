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
    applications = serializers.ListField(child=serializers.CharField(), write_only=True)
    session_id = serializers.UUIDField(required=False)

    class Meta:
        model = UserPreference
        fields = ["activities", "applications", "session_id", "budget"]

    def create(self, validated_data):
        user = self.context['request'].user
        activity_names = validated_data.pop("activities", [])
        app_names = validated_data.pop("applications", [])

        # --- REFINED CREATION LOGIC ---
        
        # Step 1: Create the base UserPreference object
        preference_data = {**validated_data}
        if user.is_authenticated:
            preference_data['user'] = user
            preference_data.pop('session_id', None)
        else:
            preference_data['session_id'] = validated_data.get('session_id', uuid.uuid4())
            
        preference = UserPreference.objects.create(**preference_data)

        # Step 2: Handle Activities
        created_activities = []
        for name in activity_names:
            # Use get_or_create for efficiency and safety
            activity, created = Activity.objects.get_or_create(
                name__iexact=name.strip(), 
                defaults={"name": name.strip()}
            )
            created_activities.append(activity)
        
        # Add all activities to the preference object at once
        if created_activities:
            preference.activities.add(*created_activities)

        # Step 3: Handle Applications
        first_activity = created_activities[0] if created_activities else None
        created_applications = []
        for app_name in app_names:
            # Use get_or_create for the application as well
            app, created = Application.objects.get_or_create(
                name__iexact=app_name.strip(),
                defaults={
                    "name": app_name.strip(),
                    # This is a much safer fallback. It creates a default activity if none exist.
                    "activity": first_activity or Activity.objects.get_or_create(name="General Use")[0],
                    "intensity_level": "medium"
                }
            )
            created_applications.append(app)
        
        if created_applications:
            preference.applications.add(*created_applications)

        return preference

class RecommendationSpecificationSerializer(serializers.ModelSerializer):
    # We define custom fields to structure the output JSON
    minimum_specs = serializers.SerializerMethodField()
    recommended_specs = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()

    class Meta:
        model = RecommendationSpecification
        fields = ["note", "minimum_specs", "recommended_specs"]

    def get_note(self, obj):
        # You can make this more dynamic later if needed
        return "A computer with the recommended specifications will fit your needs perfectly. The minimum specs are for basic usage."

    def get_minimum_specs(self, obj):
        return {
            "type": "minimum",
            "cpu": obj.min_cpu_name,
            "gpu": obj.min_gpu_name,
            "ram": obj.min_ram,
            "storage": obj.min_storage,
        }

    def get_recommended_specs(self, obj):
        return {
            "type": "recommended",
            "cpu": obj.recommended_cpu_name,
            "gpu": obj.recommended_gpu_name,
            "ram": obj.recommended_ram,
            "storage": obj.recommended_storage,
        }
