from ..models import Application, ApplicationSystemRequirement, Activity
from .ai_scraper import query_all_ais  # Updated import
from .ai_extractor import find_consensus_response  # Updated import
from .utils import get_cpu_score, get_gpu_score
from django.db import transaction


def enrich_application(application_name, activity_name=None, update_existing=False):
    app = Application.objects.filter(name__iexact=application_name).first()

    # If the app exists and we are NOT in update mode, do nothing.
    if app and not update_existing:
        return app

    # --- AI Querying (same as before) ---
    prompt = f"""..."""  # Your full prompt
    raw_responses = query_all_ais(prompt)
    try:
        structured = find_consensus_response(raw_responses)
    except ValueError as e:
        print(f"Could not enrich application '{application_name}': {e}")
        return None

    # --- KEY CHANGE: Handle Create vs. Update ---
    with transaction.atomic():
        # Get or create the Activity
        activity = None
        if activity_name:
            activity, _ = Activity.objects.get_or_create(
                name__iexact=activity_name, defaults={"name": activity_name}
            )

        # If updating, fetch the existing app object
        if update_existing and app:
            print(f"Updating existing record for {app.name}")
            app.name = structured.get("name", app.name)
            app.source = structured.get("source", app.source)
            app.intensity_level = structured.get("intensity_level", app.intensity_level)
            if activity:
                app.activity = activity
            app.save()  # The 'updated_at' field will be set automatically
        else:  # Otherwise, create a new one
            print(f"Creating new record for {application_name}")
            app = Application.objects.create(
                name=structured.get("name", application_name),
                source=structured.get("source"),
                intensity_level=structured.get("intensity_level", "medium"),
                activity=activity if activity else Activity.objects.first(),
            )

        # Delete old requirements to replace them with the new ones
        ApplicationSystemRequirement.objects.filter(application=app).delete()

        # Save each new Requirement with benchmark scores
        for req in structured.get("requirements", []):
            cpu = req.get("cpu")
            gpu = req.get("gpu")
            ApplicationSystemRequirement.objects.create(
                application=app,
                type=req.get("type"),
                cpu=cpu,
                gpu=gpu,
                cpu_score=get_cpu_score(cpu),
                gpu_score=get_gpu_score(gpu),
                ram=req.get("ram", 4),
                storage=req.get("storage", 10),
            )

    return app
