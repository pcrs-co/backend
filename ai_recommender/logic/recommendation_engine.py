# ai_recommender/logic/recommendation_engine.py
from django.db.models import F, Sum, Value, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce


# --- CHANGE 1: IMPROVED "HEAVIEST" REQUIREMENT LOGIC ---
# This new function uses a weighted score to better identify the most demanding application.
def get_heaviest_requirement(requirements_qs):
    """
    Finds the single most demanding requirement set from a queryset.
    The "heaviest" is determined by a weighted score of CPU, GPU, and RAM.
    """
    if not requirements_qs.exists():
        return None

    # Weights can be tuned. Here, CPU/GPU are considered more impactful than RAM.
    # We use Coalesce to handle potential null scores gracefully.
    heaviest_req = (
        requirements_qs.annotate(
            weighted_score=ExpressionWrapper(
                Coalesce(F("cpu_score"), Value(0)) * 1.0
                + Coalesce(F("gpu_score"), Value(0)) * 1.0
                + Coalesce(F("ram"), Value(0))
                * 25.0,  # A simple multiplier to bring RAM into a similar scale as scores
                output_field=FloatField(),
            )
        )
        .order_by("-weighted_score")
        .first()
    )

    return heaviest_req


# --- NEW HELPER FUNCTION TO REDUCE REPETITION ---
def _populate_spec_defaults(spec_level, heaviest_req, total_storage):
    """Populates a dictionary with spec details for a given level."""
    if not heaviest_req:
        return {}

    prefix = "recommended_" if spec_level == "recommended" else "min_"
    return {
        f"{prefix}cpu_name": heaviest_req.cpu,
        f"{prefix}gpu_name": heaviest_req.gpu,
        f"{prefix}cpu_score": heaviest_req.cpu_score,
        f"{prefix}gpu_score": heaviest_req.gpu_score,
        f"{prefix}ram": heaviest_req.ram,
        f"{prefix}storage_size": total_storage,  # Use the aggregated total storage
        f"{prefix}storage_type": heaviest_req.storage_type,  # Still use the heaviest app's storage *type* (e.g., SSD)
    }


def generate_recommendation(user=None, session_id=None):
    """
    Generates a complete RecommendationSpecification based on a user's preferences.
    """
    from ..models import (
        RecommendationFeedback,
        RecommendationLog,
        UserPreference,
        ApplicationSystemRequirement,
        RecommendationSpecification,
    )

    pref_filter = {}
    if user and user.is_authenticated:
        pref_filter["user"] = user
    elif session_id:
        pref_filter["session_id"] = session_id
    else:
        return None

    pref = UserPreference.objects.filter(**pref_filter).order_by("-created_at").first()

    if not pref:
        print(f"No preferences found for user/session.")
        return None

    apps = pref.applications.all()
    if not apps.exists():
        print(f"No applications found for preference {pref.id}.")
        return None

    min_reqs_qs = ApplicationSystemRequirement.objects.filter(
        application__in=apps, type="minimum"
    )
    rec_reqs_qs = ApplicationSystemRequirement.objects.filter(
        application__in=apps, type="recommended"
    )

    # --- CHANGE 2: SUM THE STORAGE REQUIREMENTS ---
    # We aggregate the storage size across all "recommended" requirements.
    total_recommended_storage = (
        rec_reqs_qs.aggregate(total_storage=Sum("storage_size"))["total_storage"] or 0
    )

    # We do the same for minimums to be consistent.
    total_minimum_storage = (
        min_reqs_qs.aggregate(total_storage=Sum("storage_size"))["total_storage"] or 0
    )

    # Find the single most demanding requirement for both minimum and recommended
    heaviest_min = get_heaviest_requirement(min_reqs_qs)
    heaviest_rec = get_heaviest_requirement(rec_reqs_qs)

    # --- CHANGE 3: USE THE HELPER FUNCTION FOR CLEANER CODE ---
    defaults = {}
    defaults.update(
        _populate_spec_defaults("minimum", heaviest_min, total_minimum_storage)
    )
    defaults.update(
        _populate_spec_defaults("recommended", heaviest_rec, total_recommended_storage)
    )

    if not defaults:
        print(f"Could not determine any specs for preference {pref.id}.")
        return None

    # The rest of the function is excellent and remains the same.
    rec_spec = RecommendationSpecification.objects.create(
        user=pref.user,
        session_id=str(pref.session_id) if not pref.user else None,
        source_preference=pref,
        **defaults,
    )
    print(f"Created new recommendation {rec_spec.id} for preference {pref.id}.")

    RecommendationFeedback.objects.create(recommendation=rec_spec)
    RecommendationLog.objects.create(
        source_preference=pref,
        final_recommendation=rec_spec,
        activities_json=list(pref.activities.values_list("name", flat=True)),
        applications_json=[
            {
                "name": app.name,
                "cpu": (
                    app.requirements.filter(type="recommended").first().cpu
                    if app.requirements.filter(type="recommended").exists()
                    else None
                ),
            }
            for app in pref.applications.all()
        ],
    )

    return rec_spec
