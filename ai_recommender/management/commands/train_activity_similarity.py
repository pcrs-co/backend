# ai_recommender/management/commands/train_activity_similarity.py

import numpy as np
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Avg, F, ExpressionWrapper, FloatField
from itertools import combinations
from ai_recommender.models import (
    Activity,
    ActivitySimilarity,
    ApplicationSystemRequirement,
)


def cosine_similarity(vec1, vec2):
    """Helper to calculate cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class Command(BaseCommand):
    help = "Calculates and stores similarity scores between all activities."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Starting activity similarity training...")
        )

        activities = list(Activity.objects.prefetch_related("applications"))
        if len(activities) < 2:
            self.stdout.write(
                self.style.WARNING(
                    "Not enough activities (< 2) to calculate similarity. Exiting."
                )
            )
            return

        # Clear old similarity data
        ActivitySimilarity.objects.all().delete()
        self.stdout.write("Cleared old similarity records.")

        # --- Pre-calculate average requirement vectors for all activities ---
        self.stdout.write("Pre-calculating average system requirement vectors...")
        avg_reqs = {}
        for activity in activities:
            req_vector = ApplicationSystemRequirement.objects.filter(
                application__in=activity.applications.all(), type="recommended"
            ).aggregate(
                avg_cpu=Avg("cpu_score"), avg_gpu=Avg("gpu_score"), avg_ram=Avg("ram")
            )
            # Create a numpy array, handling None values
            avg_reqs[activity.id] = np.array(
                [
                    req_vector["avg_cpu"] or 0,
                    req_vector["avg_gpu"] or 0,
                    req_vector["avg_ram"] or 0,
                ]
            )
        self.stdout.write("Vectors calculated.")

        # --- Calculate similarities for all unique pairs ---
        similarity_objects = []
        for act1, act2 in combinations(activities, 2):
            # 1. Jaccard Similarity (based on common apps)
            apps1 = set(act1.applications.all().values_list("id", flat=True))
            apps2 = set(act2.applications.all().values_list("id", flat=True))
            intersection = len(apps1.intersection(apps2))
            union = len(apps1.union(apps2))
            jaccard_sim = intersection / union if union > 0 else 0.0

            # 2. Requirement Similarity (based on pre-calculated vectors)
            req_sim = cosine_similarity(avg_reqs[act1.id], avg_reqs[act2.id])

            # 3. Combined Score (you can tune the weights)
            combined_score = (0.4 * jaccard_sim) + (0.6 * req_sim)

            # Create objects for bulk creation (both ways)
            similarity_objects.append(
                ActivitySimilarity(
                    source_activity=act1,
                    target_activity=act2,
                    jaccard_similarity=jaccard_sim,
                    requirement_similarity=req_sim,
                    combined_score=combined_score,
                )
            )
            similarity_objects.append(
                ActivitySimilarity(
                    source_activity=act2,
                    target_activity=act1,
                    jaccard_similarity=jaccard_sim,
                    requirement_similarity=req_sim,
                    combined_score=combined_score,
                )
            )

        self.stdout.write(
            f"Calculated {len(similarity_objects)} similarity relationships. Saving to database..."
        )
        ActivitySimilarity.objects.bulk_create(similarity_objects)

        self.stdout.write(
            self.style.SUCCESS("--- Activity similarity training complete! ---")
        )
