# ai_recommender/logic/ai_discovery.py

from ..models import (
    Activity,
    Application,
    ApplicationSystemRequirement,
    ApplicationExtractionLog,
    RequirementExtractionLog,
)
from .ai_scraper import get_ai_response
from django.db import transaction
import json


def _save_single_enriched_app_data(
    app_data: dict, activity: Activity, extraction_log: ApplicationExtractionLog
) -> Application | None:
    """
    Helper function to save the data for a single application from the AI's response.
    It handles checking for existing apps and linking them correctly.
    """
    app_name = app_data.get("name")
    if not app_name:
        return None

    try:
        with transaction.atomic():
            # Check if this application already exists.
            application, created = Application.objects.get_or_create(
                name__iexact=app_name.strip(),
                defaults={
                    "name": app_name.strip(),
                    "activity": activity,
                    "source": app_data.get("source"),
                    "intensity_level": app_data.get("intensity_level", "medium"),
                },
            )

            # If the app was newly created, it needs its requirements added.
            # --- Start of new logging logic ---
            if created:
                print(
                    f"Creating new application '{application.name}' with requirements."
                )
                requirements_data = app_data.get("requirements", [])
                for req in requirements_data:
                    # Create a log for this specific requirement extraction
                    req_log = RequirementExtractionLog.objects.create(
                        application=application,
                        source_extraction_log=extraction_log,
                        extracted_cpu=req.get("cpu"),
                        extracted_gpu=req.get("gpu"),
                    )
                    # The model's smart .save() method will handle fetching scores.
                    ApplicationSystemRequirement.objects.create(
                        application=application,
                        type=req.get("type"),
                        cpu=req.get("cpu"),
                        gpu=req.get("gpu"),
                        ram=req.get("ram", 0),
                        storage_size=req.get("storage_size", 0),
                        storage_type=req.get("storage_type", "Any"),
                    )
            else:
                # If the app already existed, just ensure it's linked to this new activity.
                print(
                    f"Application '{application.name}' already exists. Linking to activity '{activity.name}'."
                )
                application.activity = activity  # You might want to use a ManyToManyField here in the future
                application.save()

            return application
    except Exception as e:
        print(f"DATABASE ERROR while saving app '{app_name}': {e}")
        return None


def discover_and_enrich_apps_for_activity(
    activity: Activity, user_considerations: str = ""
) -> list[Application]:
    """
    Uses a single, powerful AI call to get the top 3 applications for an activity
    AND their system requirements all at once.

    Returns a list of the Application objects that were created or linked.
    """
    print(f"Starting one-shot AI discovery for activity: '{activity.name}'")

    prompt = f"""
    Give me the top 3 most popular and essential software applications for the activity: "{activity.name}".
    When selecting the applications, you MUST take the following user considerations into account:
    **User Considerations:** "{user_considerations}"
    For each application, provide its system requirements.
    Your response MUST be a single, valid JSON object. Do not add any text before or after the JSON.
    The root key must be "discovered_applications", which is an array of application objects.
    Each application object must have the following exact structure:
    {{
      "name": "Corrected App Name",
      "source": "A valid URL to the official requirements page, or null if not found",
      "intensity_level": "low, medium, or high",
      "requirements": [
        {{"type": "minimum", "cpu": "Intel Core i5-6600K", "gpu": "NVIDIA GeForce GTX 970", "ram": 8, "storage_size": 50, "storage_type": "HDD"}},
        {{"type": "recommended", "cpu": "Intel Core i7-8700K", "gpu": "NVIDIA GeForce GTX 1080 Ti", "ram": 16, "storage_size": 50, "storage_type": "SSD"}}
      ]
    }}

    Example JSON response format:
    {{
        "discovered_applications": [
            {{
                "name": "Blender",
                "source": "https://www.blender.org/download/requirements/",
                "intensity_level": "high",
                "requirements": [
                    {{"type": "minimum", "cpu": "Intel Core i3", "gpu": "NVIDIA GeForce 400 Series", "ram": 8, "storage_size": 1, "storage_type": "HDD"}},
                    {{"type": "recommended", "cpu": "Intel Core i9", "gpu": "NVIDIA GeForce RTX 3060", "ram": 32, "storage_size": 2, "storage_type": "SSD"}}
                ]
            }},
            {{
                "name": "Autodesk Maya",
                "source": null,
                "intensity_level": "high",
                "requirements": [
                    {{"type": "minimum", "cpu": "Intel Core i5", "gpu": "NVIDIA Quadro P600", "ram": 8, "storage_size": 7, "storage_type": "HDD"}},
                    {{"type": "recommended", "cpu": "Intel Core i7", "gpu": "NVIDIA Quadro RTX 4000", "ram": 16, "storage_size": 7, "storage_type": "SSD"}}
                ]
            }}
        ]
    }}
    """

    # We use ask_openai directly here as it's configured to expect JSON.
    raw_response = get_ai_response(prompt)

    if not raw_response:
        print(f"AI failed to return a response for '{activity.name}'.")
        return []

    # --- LOG THE AI's RAW RESPONSE ---
    extraction_log = ApplicationExtractionLog.objects.create(
        activity=activity, raw_ai_response=raw_response
    )

    try:
        data = json.loads(raw_response)
        applications_data = data.get("discovered_applications", [])

        processed_apps = []
        for app_data in applications_data:
            app_object = _save_single_enriched_app_data(
                app_data, activity, extraction_log
            )
            if app_object:
                processed_apps.append(app_object)

        return processed_apps

    except json.JSONDecodeError:
        print(
            f"Failed to parse JSON response from AI for activity '{activity.name}': {raw_response}"
        )
        return []
    except Exception as e:
        print(f"An unexpected error occurred during AI data processing: {e}")
        return []
