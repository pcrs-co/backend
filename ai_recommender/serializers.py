from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from rest_framework import serializers
from io import BytesIO
from .tasks import enrich_user_preference_task
from .models import *
import pandas as pd
import string
import random
import re
import uuid


class CPUBenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPUBenchmark
        fields = "__all__"


class GPUBenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPUBenchmark
        fields = "__all__"


class DiskBenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiskBenchmark
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
    """
    Handles the creation and retrieval of a UserPreference.

    On CREATE (POST):
    - Accepts 'primary_activity', 'secondary_activities', 'budget', and 'session_id'.
    - Validates the input to ensure data quality.
    - Triggers a background task to enrich the preference with application data.

    On RETRIEVE (GET):
    - Displays the preference details, including a nested list of linked activities.
    """

    # --- Fields for WRITE operations (when a user submits data) ---
    primary_activity = serializers.CharField(
        write_only=True,
        help_text="The main activity the user is interested in (e.g., 'Video Editing').",
    )
    secondary_activities = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="A list of other related activities.",
    )

    # --- Fields for READ operations (when the API returns data) ---
    activities = ActivitySerializer(many=True, read_only=True)

    # Session ID is write-only for anonymous users, but we might want to read it back.
    # The 'user' field will be automatically populated from the request context.
    session_id = serializers.UUIDField(required=False)

    # --- ADD THE NEW FIELD ---
    considerations = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UserPreference
        # Define fields for both reading and writing.
        fields = [
            "id",
            "user",
            "session_id",
            "budget",
            "created_at",
            "considerations",  # New field for user preferences
            "activities",  # For reading
            "primary_activity",
            "secondary_activities",  # For writing
        ]
        read_only_fields = ["id", "user", "created_at", "activities"]

    def validate_primary_activity(self, value):
        """Ensures the primary activity is not empty or just whitespace."""
        if not value or not value.strip():
            raise serializers.ValidationError("Primary activity cannot be empty.")
        return value.strip()

    def create(self, validated_data):
        """
        --- NEW, CORRECTED LOGIC ---
        Always creates a new UserPreference for every submission to ensure
        a clean, distinct record for each recommendation event.
        """
        user = self.context["request"].user
        primary_activity_name = validated_data.pop("primary_activity")
        secondary_activity_names = validated_data.pop("secondary_activities", [])

        # --- THIS IS THE FIX ---
        # Include 'considerations' and 'budget' when preparing data.
        preference_data = {
            "budget": validated_data.get("budget"),
            "considerations": validated_data.get(
                "considerations", ""
            ),  # Default to empty string
        }

        if user.is_authenticated:
            preference_data["user"] = user
        else:
            # For anonymous users, we still attach the session_id
            preference_data["session_id"] = validated_data.get(
                "session_id", uuid.uuid4()
            )

        # --- THE KEY CHANGE ---
        # We now ALWAYS use .create()
        preference = UserPreference.objects.create(**preference_data)

        # Activity linking logic remains the same
        all_activity_names = [primary_activity_name] + secondary_activity_names
        for activity_name in all_activity_names:
            clean_name = activity_name.strip()
            if clean_name:
                activity, _ = Activity.objects.get_or_create(
                    name__iexact=clean_name, defaults={"name": clean_name}
                )
                preference.activities.add(activity)

        return preference


# In RecommendationSpecificationSerializer


class RecommendationSpecificationSerializer(serializers.ModelSerializer):
    minimum_specs = serializers.SerializerMethodField()
    recommended_specs = serializers.SerializerMethodField()
    session_id = serializers.CharField(
        source="source_preference.session_id", read_only=True, allow_null=True
    )

    class Meta:
        model = RecommendationSpecification
        # We now pass the new fields directly
        fields = [
            "session_id",
            "ai_title",
            "ai_summary",
            "minimum_specs",
            "recommended_specs",
        ]

    # These helper methods are still great for structuring the nested spec objects
    def get_minimum_specs(self, obj):
        return {
            "type": "minimum",
            "cpu": obj.min_cpu_name or "Not determined",
            "gpu": obj.min_gpu_name or "Not determined",
            "ram_gb": obj.min_ram or 0,
            "storage_gb": obj.min_storage_size or 0,
            "storage_type": obj.min_storage_type or "Any",
        }

    def get_recommended_specs(self, obj):
        return {
            "type": "recommended",
            "cpu": obj.recommended_cpu_name or "Not determined",
            "gpu": obj.recommended_gpu_name or "Not determined",
            "ram_gb": obj.recommended_ram or 0,
            "storage_gb": obj.recommended_storage_size or 0,
            "storage_type": obj.recommended_storage_type or "Any",
        }


class SuggestionSerializer(serializers.Serializer):
    """
    A simple serializer to format the data for the frontend's autocomplete.
    """

    activities = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = ["activities"]


# ai_recommender/serializers.py
# ... (add this class to the end of the file)


class UserRecommendationHistorySerializer(serializers.ModelSerializer):
    """
    A serializer for a user's recommendation history list.
    Crucially, it mimics the structure of RecommendationSpecificationSerializer
    so the frontend can reuse the Results page component.
    """

    minimum_specs = serializers.SerializerMethodField()
    recommended_specs = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()
    # We add the activities that generated this recommendation.
    # Add a SerializerMethodField for more control
    activities = serializers.SerializerMethodField()

    class Meta:
        model = RecommendationSpecification
        fields = [
            "id",
            "created_at",
            "activities",  # Use the new method field
            "note",
            "minimum_specs",
            "recommended_specs",
        ]

    def get_activities(self, obj):
        if obj.source_preference and hasattr(obj.source_preference, "activities"):
            return list(obj.source_preference.activities.values_list("name", flat=True))
        return []  # Return an empty list if the source preference is gone

    def get_note(self, obj):
        return "This is a past recommendation. The product list below reflects current inventory."

    def get_minimum_specs(self, obj):
        """Returns the minimum spec set with safe defaults."""
        return {
            "type": "minimum",
            "cpu": obj.min_cpu_name or "N/A",
            "gpu": obj.min_gpu_name or "N/A",
            "ram_gb": obj.min_ram or 0,
            "storage_gb": obj.min_storage_size or 0,
            "storage_type": obj.min_storage_type or "Any",
        }

    def get_recommended_specs(self, obj):
        """Returns the recommended spec set with safe defaults."""
        return {
            "type": "recommended",
            "cpu": obj.recommended_cpu_name or "N/A",
            "gpu": obj.recommended_gpu_name or "N/A",
            "ram_gb": obj.recommended_ram or 0,
            "storage_gb": obj.recommended_storage_size or 0,
            "storage_type": obj.recommended_storage_type or "Any",
        }
