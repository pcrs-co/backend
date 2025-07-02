# ai_recommender/logic/matching_engine.py

from django.db.models import Q, F, Case, When, Value, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
import re

from vendor.models import Product
from ..models import RecommendationSpecification


def find_matching_products(rec_spec: RecommendationSpecification, spec_level: str):
    """
    Finds and ranks products using an efficient, score-based filtering strategy.
    It filters products where the component scores are greater than or equal to
    the target scores from the recommendation specification.
    """
    # 1. Determine the target specifications based on the desired level
    if spec_level == "minimum":
        targets = {
            "cpu_score": rec_spec.min_cpu_score,
            "gpu_score": rec_spec.min_gpu_score,
            "ram": rec_spec.min_ram,
            "storage": rec_spec.min_storage_size,
            "cpu_name": rec_spec.min_cpu_name,
        }
    else:  # Default to 'recommended'
        targets = {
            "cpu_score": rec_spec.recommended_cpu_score,
            "gpu_score": rec_spec.recommended_gpu_score,
            "ram": rec_spec.recommended_ram,
            "storage": rec_spec.recommended_storage_size,
            "cpu_name": rec_spec.recommended_cpu_name,
        }

    target_cpu_score = targets["cpu_score"] or 0
    target_gpu_score = targets["gpu_score"] or 0
    target_ram = targets["ram"] or 0
    target_storage = targets["storage"] or 0
    rec_cpu_name = targets["cpu_name"]

    # --- 2. THE CRITICAL FIX: BUILD A FAST, SCORE-BASED FILTER ---
    # This query is now extremely efficient as it filters on indexed integer fields
    # across related models.
    eligibility_filters = Q(
        processor__score__gte=target_cpu_score,
        memory__capacity_gb__gte=target_ram,
        storage__capacity_gb__gte=target_storage,
    )

    # Only add the GPU filter if a GPU is actually required (score > 0).
    if target_gpu_score > 0:
        eligibility_filters &= Q(graphic__score__gte=target_gpu_score)

    # This is now a very fast database query.
    eligible_products = Product.objects.filter(eligibility_filters)

    # --- THIS IS THE FIX for "Cannot use None" ---
    # Prepare ranking cases
    ranking_cases = [
        Coalesce(F("processor__score"), 0.0),
        Coalesce(F("graphic__score"), 0.0),
    ]
    B_BRAND, B_SERIES, B_DIRECT_MATCH = 25.0, 50.0, 100.0

    if rec_cpu_name:
        cpu_brand_match = re.search(r"(intel|amd)", rec_cpu_name, re.I)
        cpu_brand_affinity = (
            cpu_brand_match.group(1).lower() if cpu_brand_match else None
        )
        if cpu_brand_affinity:
            ranking_cases.append(
                Case(
                    When(
                        processor__brand__icontains=cpu_brand_affinity,
                        then=Value(B_BRAND),
                    ),
                    default=Value(0.0),
                )
            )

        cpu_series_match = re.search(r"(i[3579]|Ryzen\s[3579])", rec_cpu_name, re.I)
        cpu_series_affinity = (
            cpu_series_match.group(1).lower() if cpu_series_match else None
        )
        if cpu_series_affinity:
            ranking_cases.append(
                Case(
                    When(
                        processor__series__icontains=cpu_series_affinity,
                        then=Value(B_SERIES),
                    ),
                    default=Value(0.0),
                )
            )

        ranking_cases.append(
            Case(
                When(
                    processor__model__icontains=rec_cpu_name, then=Value(B_DIRECT_MATCH)
                ),
                default=Value(0.0),
            )
        )

    ranked_products = eligible_products.annotate(
        ranking_score=ExpressionWrapper(
            sum(ranking_cases),  # sum() works on a list of expression objects
            output_field=FloatField(),
        )
    ).order_by("-ranking_score", "price")

    return ranked_products
