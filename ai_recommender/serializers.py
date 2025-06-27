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


# +++ UPGRADED UserPreferenceSerializer +++
# class UserPreferenceSerializer(serializers.ModelSerializer):
#     """
#     Handles the creation and retrieval of a UserPreference.

#     On CREATE (POST):
#     - Accepts 'primary_activity', 'secondary_activities', 'budget', and 'session_id'.
#     - Validates the input to ensure data quality.
#     - Triggers a background task to enrich the preference with application data.

#     On RETRIEVE (GET):
#     - Displays the preference details, including a nested list of linked activities.
#     """

#     # --- Fields for WRITE operations (when a user submits data) ---
#     primary_activity = serializers.CharField(
#         write_only=True,
#         help_text="The main activity the user is interested in (e.g., 'Video Editing').",
#     )
#     secondary_activities = serializers.ListField(
#         child=serializers.CharField(),
#         write_only=True,
#         required=False,
#         allow_empty=True,
#         help_text="A list of other related activities.",
#     )

#     # --- Fields for READ operations (when the API returns data) ---
#     activities = ActivitySerializer(many=True, read_only=True)

#     # Session ID is write-only for anonymous users, but we might want to read it back.
#     # The 'user' field will be automatically populated from the request context.
#     session_id = serializers.UUIDField(required=False)

#     class Meta:
#         model = UserPreference
#         # Define fields for both reading and writing.
#         fields = [
#             "id",
#             "user",
#             "session_id",
#             "budget",
#             "created_at",
#             "activities",  # For reading
#             "primary_activity",
#             "secondary_activities",  # For writing
#         ]
#         read_only_fields = ["id", "user", "created_at", "activities"]

#     def validate_primary_activity(self, value):
#         """Ensures the primary activity is not empty or just whitespace."""
#         if not value or not value.strip():
#             raise serializers.ValidationError("Primary activity cannot be empty.")
#         return value.strip()

#     def create(self, validated_data):
#         """
#         Custom create logic to handle activities and trigger the background task.
#         """
#         # 1. Get the current user from the request context.
#         user = self.context["request"].user

#         # 2. Extract activity names from the validated data.
#         primary_activity_name = validated_data.pop("primary_activity")
#         secondary_activity_names = validated_data.pop("secondary_activities", [])

#         # 3. Create the core UserPreference object.
#         preference_data = {**validated_data}
#         if user.is_authenticated:
#             preference_data["user"] = user
#             # Don't save a session_id for logged-in users.
#             preference_data.pop("session_id", None)
#         else:
#             preference_data["session_id"] = validated_data.get(
#                 "session_id", uuid.uuid4()
#             )

#         preference = UserPreference.objects.create(**preference_data)

#         # 4. Process all activities, get or create them, and link to the preference.
#         all_activity_names = [primary_activity_name] + secondary_activity_names
#         for activity_name in all_activity_names:
#             # Clean up the name and skip if it's empty after stripping.
#             clean_name = activity_name.strip()
#             if clean_name:
#                 activity, _ = Activity.objects.get_or_create(
#                     name__iexact=clean_name, defaults={"name": clean_name}
#                 )
#                 preference.activities.add(activity)

#         # 5. Trigger the focused background task to discover and enrich applications.
#         #    This makes the API response immediate for the user.
#         enrich_user_preference_task.delay(
#             preference.id
#         )  # ++ FIXED: Completed the function call

#         return preference


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

    class Meta:
        model = UserPreference
        # Define fields for both reading and writing.
        fields = [
            "id",
            "user",
            "session_id",
            "budget",
            "created_at",
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
        Custom create logic to handle activities.
        This now ONLY creates the preference object and links activities.
        The AI enrichment is handled by the view that calls this serializer.
        """
        # 1. Get the current user from the request context.
        user = self.context["request"].user

        # 2. Extract activity names from the validated data.
        primary_activity_name = validated_data.pop("primary_activity")
        secondary_activity_names = validated_data.pop("secondary_activities", [])

        # 3. Create the core UserPreference object.
        preference_data = {**validated_data}
        if user.is_authenticated:
            preference_data["user"] = user
            preference_data.pop("session_id", None)
        else:
            preference_data["session_id"] = validated_data.get(
                "session_id", uuid.uuid4()
            )

        preference = UserPreference.objects.create(**preference_data)

        # 4. Process all activities, get or create them, and link to the preference.
        all_activity_names = [primary_activity_name] + secondary_activity_names
        for activity_name in all_activity_names:
            clean_name = activity_name.strip()
            if clean_name:
                activity, _ = Activity.objects.get_or_create(
                    name__iexact=clean_name, defaults={"name": clean_name}
                )
                preference.activities.add(activity)

        # --- FIX: REMOVE THE REDUNDANT BACKGROUND TASK ---
        # enrich_user_preference_task.delay(
        #     preference.id
        # )

        return preference  # Return the created preference object


# +++ UPGRADED RecommendationSpecificationSerializer +++
class RecommendationSpecificationSerializer(serializers.ModelSerializer):
    """
    Presents the final recommendation in a clean, robust, and nested JSON format
    for the frontend. Provides default values to prevent frontend errors.
    """

    minimum_specs = serializers.SerializerMethodField()
    recommended_specs = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()

    class Meta:
        model = RecommendationSpecification
        fields = ["note", "minimum_specs", "recommended_specs"]

    def get_note(self, obj):
        if not obj.recommended_cpu_name:
            return "We are still processing your request. Please check back in a few minutes to see your personalized recommendations."
        return "Based on your needs, a computer with the 'recommended' specifications will provide the best experience. The 'minimum' specs are for basic usage only."

    def get_minimum_specs(self, obj):
        """Returns the minimum spec set with safe defaults."""
        return {
            "type": "minimum",
            "cpu": obj.min_cpu_name or "Not determined",
            "gpu": obj.min_gpu_name or "Not determined",
            "ram_gb": obj.min_ram or 0,
            "storage_gb": obj.min_storage_size or 0,
            "storage_type": obj.min_storage_type or "Any",
        }

    def get_recommended_specs(self, obj):
        """Returns the recommended spec set with safe defaults."""
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
