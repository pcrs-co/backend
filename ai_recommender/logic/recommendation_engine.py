from ..models import (
    UserPreference,
    Application,
    ApplicationSystemRequirement,
    RecommendationSpecification,
)
from django.db.models import Max
from .utils import compare_requirements


def generate_recommendation(user=None, session_id=None):
    # Get preference
    pref = None
    if user:
        pref = UserPreference.objects.filter(user=user).last()
    elif session_id:
        pref = UserPreference.objects.filter(session_id=session_id).last()

    if not pref:
        return None  # No preferences found

    # Get related applications
    apps = pref.applications.all()

    if not apps.exists():  # Check if the queryset has any applications
        print("No applications found for this preference.")
        return None

    # Gather all requirements
    min_requirements = ApplicationSystemRequirement.objects.filter(
        application__in=apps, type="minimum"
    )
    rec_requirements = ApplicationSystemRequirement.objects.filter(
        application__in=apps, type="recommended"
    )

    min_specs = compare_requirements(min_requirements)
    rec_specs = compare_requirements(rec_requirements)

    rec, created = RecommendationSpecification.objects.update_or_create(
        user=user,
        session_id=str(session_id) if not user else None,
        defaults={
            "min_cpu_score": min_specs["cpu_score"],
            "min_gpu_score": min_specs["gpu_score"],
            "min_ram": min_specs["ram"],
            "min_storage": min_specs["storage"],
            "min_cpu_name": min_specs["cpu_name"],  # New
            "min_gpu_name": min_specs["gpu_name"],  # New
            "recommended_cpu_score": rec_specs["cpu_score"],
            "recommended_gpu_score": rec_specs["gpu_score"],
            "recommended_ram": rec_specs["ram"],
            "recommended_storage": rec_specs["storage"],
            "recommended_cpu_name": rec_specs["cpu_name"],  # New
            "recommended_gpu_name": rec_specs["gpu_name"],  # New
            "source_preference": pref,  # Good practice to link it
        },
    )

    return rec
