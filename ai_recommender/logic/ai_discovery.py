from .ai_scraper import query_all_ais
from .ai_extractor import find_consensus_response, extract_requirements_from_response
from ..models import (
    Application,
    Activity,
    RequirementExtractionLog,
    ApplicationExtractionLog,
)
import json


def discover_applications_for_activity(activity: Activity):
    """
    Uses AI to find a list of common applications for a given activity.
    """
    prompt = f"""
    List the top 15 most popular and essential software applications for the activity: "{activity.name}".
    Your response MUST be a single, valid JSON object with a single key "applications" which is an array of strings.
    Example: {{"applications": ["Application One", "Application Two", "Another App"]}}
    """

    # We can use a single, reliable AI for this as it's less critical than specs
    from .ai_scraper import ask_openai

    raw_response = ask_openai(prompt)

    try:
        data = json.loads(raw_response)
        app_names = data.get("applications", [])

        # Log this discovery event
        ApplicationExtractionLog.objects.create(
            activity=activity,
            source_text=prompt,  # Log the prompt for traceability
            extracted_apps={"applications": app_names},
            method="openai-discovery",
            confidence=0.9,  # High confidence as it's a discovery task
        )
        return app_names
    except (json.JSONDecodeError, AttributeError):
        return []


def discover_and_save_requirements(app_name: str, activity: Activity):
    """
    This is the main enrichment function. It finds system requirements for a single application
    and saves them to the database. It now handles both creation and updates.
    """
    from .utils import get_cpu_score, get_gpu_score
    from django.db import transaction

    # Check if the app already exists
    app = Application.objects.filter(name__iexact=app_name).first()

    prompt = f"""
    Give me the system requirements for the application: "{app_name}".
    Provide both "minimum" and "recommended" specifications.
    Your response MUST be a single, valid JSON object with the following structure. Do not add any text before or after the JSON.
    {{
      "name": "Corrected App Name",
      "source": "A valid URL to the official requirements page",
      "intensity_level": "low, medium, or high",
      "requirements": [
        {{"type": "minimum", "cpu": "Intel Core i5-6600K", "gpu": "NVIDIA GeForce GTX 970", "ram": 8, "storage": 50}},
        {{"type": "recommended", "cpu": "Intel Core i7-8700K", "gpu": "NVIDIA GeForce GTX 1080 Ti", "ram": 16, "storage": 50}}
      ]
    }}
    """

    raw_responses = query_all_ais(prompt)

    try:
        structured = find_consensus_response(raw_responses)
    except ValueError as e:
        print(f"Could not get consensus for '{app_name}': {e}")
        return None  # Abort if we can't get good data

    with transaction.atomic():
        if not app:  # If the application is new
            app = Application.objects.create(
                name=structured.get("name", app_name),
                source=structured.get("source"),
                intensity_level=structured.get("intensity_level", "medium"),
                activity=activity,
            )
        else:  # If we are updating an existing application
            app.source = structured.get("source", app.source)
            app.intensity_level = structured.get("intensity_level", app.intensity_level)
            app.save()  # This will automatically update the `modified_at` timestamp

        # Log the successful extraction for this application
        RequirementExtractionLog.objects.create(
            application=app,
            source_text="\n---\n".join(raw_responses),  # Log all AI responses
            extracted_json=structured,
            method="multi-ai-consensus",
        )

        # Delete old requirements and create the new, updated ones
        app.requirements.all().delete()
        for req in structured.get("requirements", []):
            cpu_name = req.get("cpu")
            gpu_name = req.get("gpu")

            # The .save() method on the model will handle fetching scores
            app.requirements.create(
                type=req.get("type"),
                cpu=cpu_name,
                gpu=gpu_name,
                ram=req.get("ram", 0),
                storage=req.get("storage", 0),
                notes=req.get("notes", ""),
            )
    return app
