import re
from login_and_register.models import *
from django.db.models import Q
from django.db import models
from .logic.web_extractor import get_structured_component
from django.db.models import Avg
import difflib
import uuid


class Activity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def get_application_set(self):
        """Helper to get a set of primary keys for this activity's apps."""
        return set(self.applications.values_list("pk", flat=True))

    def get_similarity_with(self, other_activity):
        """
        Calculates a similarity score between this activity and another.

        Returns a dictionary containing different similarity metrics.
        """
        if not isinstance(other_activity, Activity):
            raise TypeError("Can only compare with another Activity instance.")

        # --- Metric 1: Jaccard Similarity based on shared applications ---
        my_apps = self.get_application_set()
        other_apps = other_activity.get_application_set()

        if not my_apps or not other_apps:
            jaccard_similarity = 0.0
        else:
            intersection_size = len(my_apps.intersection(other_apps))
            union_size = len(my_apps.union(other_apps))
            jaccard_similarity = (
                intersection_size / union_size if union_size > 0 else 0.0
            )

        # --- Metric 2: Similarity based on average system requirements ---
        # This calculates an "average performance fingerprint" for an activity.
        my_avg_scores = self.applications.aggregate(
            avg_cpu=Avg("requirements__cpu_score"),
            avg_gpu=Avg("requirements__gpu_score"),
        )
        other_avg_scores = other_activity.applications.aggregate(
            avg_cpu=Avg("requirements__cpu_score"),
            avg_gpu=Avg("requirements__gpu_score"),
        )

        # Calculate a simple distance (lower is more similar). We normalize by the max.
        # Avoid division by zero.
        cpu_diff = 0
        if my_avg_scores["avg_cpu"] and other_avg_scores["avg_cpu"]:
            diff = abs(my_avg_scores["avg_cpu"] - other_avg_scores["avg_cpu"])
            # Normalize the difference to be between 0 and 1
            cpu_diff = diff / max(my_avg_scores["avg_cpu"], other_avg_scores["avg_cpu"])

        # We can create a combined score, weighting Jaccard more heavily.
        # A simple approach: 70% Jaccard, 30% Requirement similarity
        # (Note: Requirement similarity is 1 - normalized_difference)
        requirement_similarity = 1 - cpu_diff
        combined_score = (0.7 * jaccard_similarity) + (0.3 * requirement_similarity)

        return {
            "jaccard_similarity": round(jaccard_similarity, 3),
            "requirement_similarity": round(requirement_similarity, 3),
            "combined_score": round(combined_score, 3),
            "my_avg_cpu": my_avg_scores["avg_cpu"],
            "other_avg_cpu": other_avg_scores["avg_cpu"],
        }


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
    cpu = models.CharField(
        max_length=255,
        unique=True,
        help_text="The full, original name from the benchmark source.",
    )

    # Structured data fields that can be null if info is not available
    model_name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="The clean model name, e.g., 'Intel Core i9-9960X'",
    )
    clock_speed_ghz = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The clock speed in GHz, if available.",
    )
    score = models.IntegerField()
    rank = models.IntegerField(null=True, blank=True)
    value_score = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    embedding = models.TextField(
        blank=True, null=True, help_text="JSON-serialized 768-dim vector embedding."
    )

    def save(self, *args, **kwargs):
        # --- UNCOMMENT AND FIX ---
        if not self.model_name:
            # CORRECT: Use self.cpu, not self.name
            clean_name = self.cpu.strip()
            if "@" in clean_name:
                parts = clean_name.split("@", 1)
                self.model_name = parts[0].strip()
                speed_match = re.search(r"(\d+\.?\d*)\s*GHz", parts[1], re.IGNORECASE)
                if speed_match:
                    self.clock_speed_ghz = float(speed_match.group(1))
                else:
                    self.clock_speed_ghz = None
            else:
                self.model_name = clean_name
                self.clock_speed_ghz = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.cpu


class GPUBenchmark(models.Model):
    gpu = models.CharField(
        max_length=255,
        unique=True,
        help_text="The full, original name from the benchmark source, e.g., 'NVIDIA GeForce RTX 4090'",
    )
    model_name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="The clean model name, e.g., 'GeForce RTX 4090'",
    )
    score = models.IntegerField()
    rank = models.IntegerField(null=True, blank=True)
    value_score = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    embedding = models.TextField(
        blank=True, null=True, help_text="JSON-serialized 768-dim vector embedding."
    )

    def save(self, *args, **kwargs):
        # --- UNCOMMENT AND FIX ---
        if not self.model_name:
            # CORRECT: Use self.gpu, not self.name
            clean_name = self.gpu.strip()
            prefixes_to_remove = ["NVIDIA", "AMD", "Intel"]
            parsed_model_name = clean_name
            for prefix in prefixes_to_remove:
                if parsed_model_name.lower().startswith(prefix.lower()):
                    parsed_model_name = parsed_model_name[len(prefix) :].strip()
            self.model_name = parsed_model_name
        super().save(*args, **kwargs)

    def __str__(self):
        # Using self.gpu is better here as it's the full, original name
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


# +++ OVERHAULED ApplicationSystemRequirement MODEL +++
class ApplicationSystemRequirement(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="requirements"
    )
    type = models.CharField(
        max_length=20, choices=[("minimum", "Minimum"), ("recommended", "Recommended")]
    )
    cpu = models.CharField(max_length=255)
    gpu = models.CharField(max_length=255)
    cpu_score = models.IntegerField(null=True, blank=True)
    gpu_score = models.IntegerField(null=True, blank=True)
    ram = models.IntegerField(help_text="RAM in GB")
    storage_size = models.IntegerField(help_text="Storage in GB")
    storage_type = models.CharField(
        max_length=10,
        choices=[("SSD", "SSD"), ("HDD", "HDD"), ("Any", "Any")],
        default="Any",
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    ### REFACTORED AND SIMPLIFIED METHOD ###
    def _get_benchmark_score(self, requirement_name, benchmark_model, component_type):
        from .logic.utils import find_best_benchmark_object

        """
        Finds the best benchmark score by calling the canonical lookup function.
        This is now a simple wrapper.
        """
        print(f"--- Analyzing {component_type} requirement: '{requirement_name}' ---")

        # The new function handles splitting and finding the best match all in one go!
        best_match_object = find_best_benchmark_object(requirement_name, component_type)

        if best_match_object:
            score = best_match_object.score
            print(
                f"--> Match found: '{best_match_object.name}'. Selected score: {score}"
            )
            return score
        else:
            print(f"CRITICAL: Could not determine a score for '{requirement_name}'.")
            return None

    def save(self, *args, **kwargs):
        """
        Orchestrates finding scores for CPU and GPU using the new,
        smarter embedding-based matching function.
        """
        from .logic.utils import find_best_benchmark_object

        print(f"--- Analyzing cpu requirement: '{self.cpu}' ---")
        if self.cpu and self.cpu_score is None:
            # Use the new, imported function
            best_cpu_match = find_best_benchmark_object(self.cpu, "cpu")
            if best_cpu_match:
                self.cpu_score = best_cpu_match.score
                print(
                    f"  -> Match found for CPU '{self.cpu}': '{best_cpu_match.cpu}' with score {best_cpu_match.score}"
                )
            else:
                print(f"  -> CRITICAL: No CPU match found for '{self.cpu}'.")

        print(f"--- Analyzing gpu requirement: '{self.gpu}' ---")
        if self.gpu and self.gpu_score is None:
            # Use the new, imported function
            best_gpu_match = find_best_benchmark_object(self.gpu, "gpu")
            if best_gpu_match:
                self.gpu_score = best_gpu_match.score
                print(
                    f"  -> Match found for GPU '{self.gpu}': '{best_gpu_match.gpu}' with score {best_gpu_match.score}"
                )
            else:
                print(f"  -> CRITICAL: No GPU match found for '{self.gpu}'.")

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
    considerations = models.TextField(
        blank=True,
        help_text="User's other preferences, e.g., 'lightweight', 'budget around $1000'.",
    )
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


class ScrapingLog(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    source = models.CharField(max_length=50)
    app_count = models.PositiveIntegerField()
    timestamp = models.DateTimeField()


class RecommendationLog(models.Model):
    """
    Records every recommendation generated by the system, creating a history
    of the AI's decisions for review and learning.
    """

    # Link to the user/session that triggered this
    source_preference = models.ForeignKey(
        UserPreference, on_delete=models.SET_NULL, null=True, blank=True
    )

    # The final recommendation that was generated
    final_recommendation = models.ForeignKey(
        RecommendationSpecification, on_delete=models.CASCADE
    )

    # A snapshot of the key inputs at the time of recommendation
    activities_json = models.JSONField(help_text="Snapshot of activity names")
    applications_json = models.JSONField(
        help_text="Snapshot of application data that was considered"
    )

    # The crucial field for feedback
    RATING_CHOICES = [
        (3, "Excellent"),  # AI was perfect
        (2, "Good"),  # Mostly correct, minor issues
        (1, "Poor"),  # Logically derived but not user-friendly or practical
        (0, "Incorrect"),  # The recommendation was just wrong
    ]
    admin_rating = models.IntegerField(
        choices=RATING_CHOICES, null=True, blank=True, db_index=True
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Why this rating was given, e.g., 'Recommended a Pentium 4, which is too old.'",
    )

    reviewed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for Rec {self.final_recommendation_id} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ApplicationExtractionLog(models.Model):
    # This logs the LLM's raw output for an activity
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    raw_ai_response = models.TextField()  # More descriptive name
    created_at = models.DateTimeField(auto_now_add=True)


class RequirementExtractionLog(models.Model):
    # This logs the specific requirements extracted for ONE application
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    # Link back to the broader AI call
    source_extraction_log = models.ForeignKey(
        ApplicationExtractionLog, on_delete=models.CASCADE, null=True, blank=True
    )
    extracted_cpu = models.CharField(max_length=255, null=True, blank=True)
    extracted_gpu = models.CharField(max_length=255, null=True, blank=True)
    extracted_ram = models.IntegerField(null=True, blank=True)
    extracted_storage = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    # This is the raw text that was processed to extract these requirements
    raw_text = models.TextField(
        null=True,
        blank=True,
        help_text="The raw text that was processed to extract these requirements.",
    )
    # This is the timestamp of when the extraction was performed
    # It helps track when the requirements were last updated
    created_at = models.DateTimeField(auto_now_add=True)


class AdminCorrectionLog(models.Model):
    # This is your KEY model for Level 1 Feedback
    # It corrects a specific component match
    requirement_log = models.ForeignKey(
        RequirementExtractionLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="correction_logs",
    )

    # What component was being corrected?
    component_type = models.CharField(
        max_length=10,
        choices=[("cpu", "CPU"), ("gpu", "GPU"), ("disk", "Disk")],
        help_text="The type of component being corrected (CPU, GPU, Disk).",
        null=True,
        blank=True,
    )
    original_text = models.CharField(
        max_length=255,
        help_text="The text the AI tried to match.",
        null=True,
        blank=True,
    )

    # What the AI matched it to (can be null if it failed)
    original_match = models.ForeignKey(
        CPUBenchmark,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="original_cpu_matches",
    )
    # NOTE: You'll need to add a similar FK for GPU if you correct both at once, but one at a time is simpler.

    # What the admin corrected it to
    corrected_match = models.ForeignKey(
        CPUBenchmark,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="corrected_cpu_matches",
    )

    reason = models.TextField(blank=True)
    corrected_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


# --- THIS IS THE NEW MODEL FOR LEVEL 2 FEEDBACK ---
# It's a simplified version of what I proposed before, to fit your structure.
class RecommendationFeedback(models.Model):
    """
    Grades the final output of a recommendation. This is the 'user-friendliness' check.
    """

    recommendation = models.OneToOneField(
        RecommendationSpecification, on_delete=models.CASCADE, primary_key=True
    )

    RATING_CHOICES = [(3, "Excellent"), (2, "Good"), (1, "Poor"), (0, "Incorrect")]
    admin_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Why this rating was given.")

    reviewed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Feedback for Rec #{self.recommendation.id}"
