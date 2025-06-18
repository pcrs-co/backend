from ai_recommender.models import (
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
    apps = []
    if pref.applications:
        app_names = [name.strip() for name in pref.applications.split(",")]
        apps = Application.objects.filter(name__in=app_names)
    if not apps:
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

    # Save to DB
    rec = RecommendationSpecification.objects.create(
        user=user,
        session_id=str(session_id) if not user else None,
        min_cpu_score=min_specs["cpu_score"],
        min_gpu_score=min_specs["gpu_score"],
        min_ram=min_specs["ram"],
        min_storage=min_specs["storage"],
        recommended_cpu_score=rec_specs["cpu_score"],
        recommended_gpu_score=rec_specs["gpu_score"],
        recommended_ram=rec_specs["ram"],
        recommended_storage=rec_specs["storage"],
    )

    return rec
