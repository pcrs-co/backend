# ai_recommender/logic/recommendation_engine.py
from django.db.models import F, Max


def get_heaviest_requirement(requirements_qs):
    """
    Finds the single most demanding requirement set from a queryset.
    The "heaviest" is determined by the highest combined CPU and GPU score.
    """
    if not requirements_qs.exists():
        return None

    # Use annotation to find the requirement with the highest combined score
    heaviest_req = (
        requirements_qs.annotate(total_score=F("cpu_score") + F("gpu_score"))
        .order_by("-total_score")
        .first()
    )

    return heaviest_req


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
        return None  # Cannot proceed without a user or session

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

    # Find the single most demanding requirement for both minimum and recommended
    heaviest_min = get_heaviest_requirement(min_reqs_qs)
    heaviest_rec = get_heaviest_requirement(rec_reqs_qs)

    defaults = {}
    if heaviest_min:
        defaults.update(
            {
                "min_cpu_name": heaviest_min.cpu,
                "min_gpu_name": heaviest_min.gpu,
                "min_cpu_score": heaviest_min.cpu_score,
                "min_gpu_score": heaviest_min.gpu_score,
                "min_ram": heaviest_min.ram,
                "min_storage_size": heaviest_min.storage_size,
                "min_storage_type": heaviest_min.storage_type,
            }
        )

    if heaviest_rec:
        defaults.update(
            {
                "recommended_cpu_name": heaviest_rec.cpu,
                "recommended_gpu_name": heaviest_rec.gpu,
                "recommended_cpu_score": heaviest_rec.cpu_score,
                "recommended_gpu_score": heaviest_rec.gpu_score,
                "recommended_ram": heaviest_rec.ram,
                "recommended_storage_size": heaviest_rec.storage_size,
                "recommended_storage_type": heaviest_rec.storage_type,
            }
        )

    if not defaults:
        print(f"Could not determine any specs for preference {pref.id}.")
        return None

    # Create the final recommendation object
    rec, created = RecommendationSpecification.objects.update_or_create(
        user=pref.user,
        session_id=str(pref.session_id) if not pref.user else None,
        defaults={"source_preference": pref, **defaults},
    )

    if created:
        # If we created a new recommendation, create a blank feedback form for it.
        RecommendationFeedback.objects.create(recommendation=rec)
        print(f"Created blank feedback form for new recommendation {rec.id}.")

    print(
        f"{'Created' if created else 'Updated'} recommendation {rec.id} for preference {pref.id}."
    )
    # --- THIS IS THE NEW LEARNING STEP ---
    # Create a log entry of this decision for later review.
    # We only create a new log, we never update an old one.
    RecommendationLog.objects.create(
        source_preference=pref,
        final_recommendation=rec,
        activities_json=list(pref.activities.values_list("name", flat=True)),
        applications_json=[
            {
                "name": app.name,
                "min_cpu": (
                    app.requirements.filter(type="minimum").first().cpu
                    if app.requirements.filter(type="minimum").exists()
                    else None
                ),
                "rec_cpu": (
                    app.requirements.filter(type="recommended").first().cpu
                    if app.requirements.filter(type="recommended").exists()
                    else None
                ),
            }
            for app in apps
        ],
    )
    print(f"Created RecommendationLog for recommendation {rec.id}.")
    # --- END OF NEW LEARNING STEP ---

    return rec
