# ai_recommender/logic/matching_engine.py

from django.db.models import Q, F, Case, When, Value, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
import re

from vendor.models import Product
from ..models import RecommendationSpecification, CPUBenchmark, GPUBenchmark


def find_matching_products(rec_spec: RecommendationSpecification, spec_level: str):
    """
    Finds and ranks products using a two-pronged strategy:
    1. Pre-selects all benchmarked components that meet the minimum performance score.
    2. Filters the product inventory for items that contain these eligible components by name.
    3. Ranks the final list of eligible products intelligently.
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

    # 2. Get all candidate component NAMES that are powerful enough
    # The name of the CPU in the benchmark table is 'cpu'
    candidate_cpu_names = list(
        CPUBenchmark.objects.filter(score__gte=target_cpu_score).values_list(
            "cpu", flat=True
        )
    )

    # The name of the GPU in the benchmark table is 'gpu'
    candidate_gpu_names = list(
        GPUBenchmark.objects.filter(score__gte=target_gpu_score).values_list(
            "gpu", flat=True
        )
    )

    # 3. Build the eligibility filter using the correct field names
    # This filter ensures that a product's components are in the pre-approved list
    # and that it meets the RAM/storage requirements.

    eligibility_filters = Q(
        # The raw text name for a product's processor is in the 'data_received' field
        processor__data_received__in=candidate_cpu_names,
        memory__capacity_gb__gte=target_ram,
        storage__capacity_gb__gte=target_storage,
    )

    # Only add the GPU filter if a GPU is actually required
    if target_gpu_score > 0 and candidate_gpu_names:
        # The raw text name for a product's graphic card is in the 'data_received' field
        eligibility_filters &= Q(graphic__data_received__in=candidate_gpu_names)

    eligible_products = Product.objects.filter(eligibility_filters)

    # 4. Rank the eligible products for best presentation
    cpu_brand_match = (
        re.search(r"(intel|amd)", rec_cpu_name, re.I) if rec_cpu_name else None
    )
    cpu_brand_affinity = cpu_brand_match.group(1).lower() if cpu_brand_match else None

    cpu_series_match = (
        re.search(r"(i[3579]|Ryzen\s[3579])", rec_cpu_name, re.I)
        if rec_cpu_name
        else None
    )
    cpu_series_affinity = (
        cpu_series_match.group(1).lower() if cpu_series_match else None
    )

    B_BRAND, B_SERIES, B_DIRECT_MATCH = 25.0, 50.0, 100.0

    # We now query on the related component's 'score' field directly
    ranked_products = eligible_products.annotate(
        ranking_score=ExpressionWrapper(
            Coalesce(F("processor__score"), 0.0)
            + Coalesce(F("graphic__score"), 0.0)
            + Case(
                When(
                    processor__brand__icontains=cpu_brand_affinity, then=Value(B_BRAND)
                ),
                default=Value(0.0),
            )
            + Case(
                When(
                    processor__series__icontains=cpu_series_affinity,
                    then=Value(B_SERIES),
                ),
                default=Value(0.0),
            )
            + Case(
                When(
                    # For a direct match, we check if the recommended name is IN the product's component model name
                    processor__model__icontains=rec_cpu_name,
                    then=Value(B_DIRECT_MATCH),
                ),
                default=Value(0.0),
            ),
            output_field=FloatField(),
        )
    ).order_by("-ranking_score", "price")

    return ranked_products
