import re
from login_and_register.models import *
from django.db.models import Q
from django.db import models
from .logic.web_extractor import get_structured_component
import difflib
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


# +++ NEW HELPER FUNCTION FOR SMART MATCHING +++
def find_best_benchmark_match(target_name: str, benchmark_model):
    """
    Finds the best benchmark record by first finding the highest string similarity,
    and then using the performance score as a tie-breaker.

    Args:
        target_name (str): The name from the AI (e.g., "Intel Core i7-8700K").
        benchmark_model: The Django model to search (CPUBenchmark or GPUBenchmark).

    Returns:
        The best matching benchmark object or None.
    """
    if not target_name:
        return None

    all_benchmarks = benchmark_model.objects.all()
    if not all_benchmarks:
        return None

    best_similarity = 0.0
    best_matches = []

    # Step 1: Find the highest similarity ratio
    for bench in all_benchmarks:
        # The name field is either 'cpu' or 'gpu'
        name_field = "cpu" if benchmark_model == CPUBenchmark else "gpu"
        similarity = difflib.SequenceMatcher(
            None, target_name.lower(), getattr(bench, name_field).lower()
        ).ratio()

        if similarity > best_similarity:
            best_similarity = similarity
            best_matches = [bench]
        elif similarity == best_similarity:
            best_matches.append(bench)

    # Step 2: If the best similarity is reasonably high, proceed
    SIMILARITY_THRESHOLD = 0.7  # Avoids matching completely unrelated things
    if best_similarity < SIMILARITY_THRESHOLD:
        print(
            f"No good match found for '{target_name}'. Highest similarity was {best_similarity:.2f}, which is below threshold."
        )
        return None

    # Step 3: From the best matches, pick the one with the highest score as a tie-breaker
    if not best_matches:
        return None

    winner = max(best_matches, key=lambda b: b.score)
    return winner


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

    def _get_benchmark_score(self, requirement_name, benchmark_model, component_type):
        """
        Finds a benchmark score by splitting a requirement string by 'or', '/', or ',',
        finding the best match for each part, and returning the highest score found.
        """
        if not requirement_name or not requirement_name.strip():
            return None

        # +++ THE CORRECTED REGEX +++
        # This regex looks for:
        # \s+or\s+  -> The whole word "or" surrounded by one or more spaces.
        # |          -> OR
        # \s*/\s*    -> A forward slash, with optional spaces around it.
        # |          -> OR
        # \s*,\s*    -> A comma, with optional spaces around it.
        # The re.IGNORECASE flag handles "Or", "OR", etc.
        separators = r"\s+or\s+|\s*/\s*|\s*,\s*"
        component_parts = re.split(separators, requirement_name, flags=re.IGNORECASE)
        # +++ END OF CORRECTION +++

        # Filter out any empty strings that might result from splitting
        component_parts = [part for part in component_parts if part and part.strip()]

        found_scores = []
        print(f"Splitting '{requirement_name}' into: {component_parts}")

        for part in component_parts:
            clean_part = part.strip()
            if not clean_part:
                continue

            # This part of your logic is already good!
            best_match_obj = find_best_benchmark_match(clean_part, benchmark_model)
            if best_match_obj:
                # The name field is either 'cpu' or 'gpu'
                name_field = "cpu" if benchmark_model == CPUBenchmark else "gpu"
                print(
                    f"  -> Match found for part '{clean_part}': '{getattr(best_match_obj, name_field)}' with score {best_match_obj.score}"
                )
                found_scores.append(best_match_obj.score)
            else:
                print(f"  -> No match found for part '{clean_part}'.")

        if found_scores:
            highest_score = max(found_scores)
            print(
                f"Found scores {found_scores}. Selecting the highest: {highest_score}"
            )
            return highest_score

        print(f"CRITICAL: Could not find a score for any part of '{requirement_name}'.")
        return None

    def save(self, *args, **kwargs):
        """
        Orchestrates finding scores for CPU and GPU. This part remains unchanged
        as it correctly calls the helper function whose logic we just updated.
        """
        if self.cpu and self.cpu_score is None:
            self.cpu_score = self._get_benchmark_score(self.cpu, CPUBenchmark, "CPU")

        if self.gpu and self.gpu_score is None:
            self.gpu_score = self._get_benchmark_score(self.gpu, GPUBenchmark, "GPU")

        # Final check to prevent DB error if everything failed
        if self.cpu_score is None or self.gpu_score is None:
            print(
                f"WARNING: Could not determine a score for CPU or GPU for '{self.application.name} ({self.type})'. Saving with null values."
            )

        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     """Orchestrates finding scores for CPU and GPU using the new structured method."""
    #     if self.cpu and self.cpu_score is None:
    #         # ++ USE THE NEW SMARTER FUNCTION ++
    #         best_match_obj = get_structured_component(self.cpu, "CPU")
    #         if best_match_obj:
    #             self.cpu_score = best_match_obj.score

    #     if self.gpu and self.gpu_score is None:
    #         # ++ USE THE NEW SMARTER FUNCTION ++
    #         best_match_obj = get_structured_component(self.gpu, "GPU")
    #         if best_match_obj:
    #             self.gpu_score = best_match_obj.score

    #     super().save(*args, **kwargs)

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
