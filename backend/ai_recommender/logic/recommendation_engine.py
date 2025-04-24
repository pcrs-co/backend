from ai_recommender.models import *
from django.db.models import Q
import uuid


def generate_spec_range(session_or_user_id):
    """
    Generates a spec range (min to max) based on user's answered activities and matched applications.
    Accepts a user ID or session ID to support both authenticated and anonymous users.
    """
    # Determine user preference based on session or user ID
    preferences = UserPreference.objects.filter(
        Q(user_id=session_or_user_id) | Q(session_id=session_or_user_id)
    )
    if not preferences.exists():
        return {"error": "No user preference found for this session/user."}

    preference = preferences.latest("created_at")  # In case of multiple
    activities = preference.activities.all()

    # Collect system requirements for all applications linked to those activities
    requirements = ApplicationSystemRequirement.objects.filter(
        application__activity__in=activities
    )

    if not requirements.exists():
        return {"error": "No system requirements found for the selected activities."}

    # Get numeric ranges for ram and storage
    ram_values = [r.ram for r in requirements]
    storage_values = [r.storage for r in requirements]

    # Extract CPUs and GPUs for benchmarking purposes
    cpu_values = list(set([r.cpu for r in requirements]))
    gpu_values = list(set([r.gpu for r in requirements]))

    return {
        "cpu_range": cpu_values,  # Later matched to CPU benchmark scores
        "gpu_range": gpu_values,  # Later matched to GPU benchmark scores
        "ram_range": {
            "min": min(ram_values),
            "max": max(ram_values),
        },
        "storage_range": {
            "min": min(storage_values),
            "max": max(storage_values),
        },
        "activities": [a.name for a in activities],
    }
