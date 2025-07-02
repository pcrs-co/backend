# ai_recommender/management/commands/reinforce_learning.py

from django.core.management.base import BaseCommand
from django.db import transaction
from ai_recommender.models import (
    AdminCorrectionLog,
    RecommendationFeedback,
    CPUBenchmark,
)
from sentence_transformers import SentenceTransformer, util
import json
import numpy as np


class Command(BaseCommand):
    help = "Reinforces AI models based on admin feedback and corrections."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("--- Starting AI Reinforcement Learning ---")
        )

        # --- Part 1: Learning from Component Corrections ---
        self.stdout.write("\n[1/2] Analyzing admin component corrections...")

        # We can implement a simple learning rule here. For example, if an admin
        # repeatedly corrects a certain text to a specific CPU, we could create
        # a "hard-coded" rule or a synonym model in the future.
        # For now, we will just report the corrections.

        corrections = AdminCorrectionLog.objects.select_related("corrected_match").all()
        if not corrections.exists():
            self.stdout.write(
                self.style.WARNING(
                    "No admin corrections found. Skipping component learning."
                )
            )
        else:
            self.stdout.write(f"Found {corrections.count()} corrections to analyze.")
            # In a more advanced version, you would use these corrections to fine-tune
            # the embedding model or create a synonym dictionary.
            # For now, this is a placeholder for that logic.
            self.stdout.write(
                self.style.SUCCESS(
                    "Component correction analysis complete (simulation)."
                )
            )

        # --- Part 2: Learning from Overall Recommendation Ratings ---
        self.stdout.write("\n[2/2] Analyzing overall recommendation feedback...")

        poor_feedback = RecommendationFeedback.objects.filter(
            admin_rating__in=[0, 1]
        )  # 0=Incorrect, 1=Poor

        if not poor_feedback.exists():
            self.stdout.write(
                self.style.WARNING(
                    "No 'Poor' or 'Incorrect' ratings found. Skipping recommendation rule tuning."
                )
            )
        else:
            self.stdout.write(
                self.style.NOTICE(
                    f"Found {poor_feedback.count()} poorly rated recommendations to learn from."
                )
            )

            # LEARNING RULE: Identify underpowered recommendations
            # Let's find out the average score of CPUs in 'Excellent' recommendations
            # to set a new baseline.
            excellent_recs = RecommendationFeedback.objects.filter(
                admin_rating=3
            ).select_related("recommendation")
            if excellent_recs.count() > 5:  # Only learn if we have enough good examples

                excellent_scores = [
                    fb.recommendation.recommended_cpu_score
                    for fb in excellent_recs
                    if fb.recommendation.recommended_cpu_score
                ]

                if excellent_scores:
                    avg_excellent_score = sum(excellent_scores) / len(excellent_scores)

                    # Propose a new system-wide minimum score threshold
                    new_threshold = int(
                        avg_excellent_score * 0.5
                    )  # e.g., 50% of the average 'excellent' score

                    self.stdout.write(
                        self.style.SUCCESS(f"Learning from excellent ratings...")
                    )
                    self.stdout.write(
                        f"  - Average CPU score in 'Excellent' recommendations: {avg_excellent_score:,.0f}"
                    )
                    self.stdout.write(
                        self.style.NOTICE(
                            f"  - PROPOSED NEW RULE: Recommend CPUs with a score of at least {new_threshold:,.0f} to avoid 'user-unfriendly' suggestions like Pentium 4."
                        )
                    )

                    # In a real system, you would save this `new_threshold` to a system
                    # settings model to be used by the recommendation engine.

        self.stdout.write(
            self.style.SUCCESS("\n--- AI Reinforcement Learning Complete ---")
        )
