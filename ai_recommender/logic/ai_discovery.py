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
            if created or not application.requirements.exists():
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
    Uses a single, powerful AI call to get up to 3 applications for an activity
    AND their system requirements all at once.
    """
    print(f"Starting one-shot AI discovery for activity: '{activity.name}'")

    if user_considerations and user_considerations.strip():
        considerations_instruction = f"""
        **User Needs (Mandatory Filter):** You must filter your choices based on these user needs: "{user_considerations}". For example, if the user mentions a budget, you MUST select free-to-play or less demanding games.
        """
    else:
        considerations_instruction = "**User Needs (Mandatory Filter):** None provided. Select the most standard, graphically intensive examples."

    # --- THE NEW, MORE EFFECTIVE PROMPT ---
    prompt = f"""
    You are an expert PC hardware analyst. Your task is to identify up to 3 specific **software titles or video games** that are excellent examples for the user's primary activity: **"{activity.name}"**.

    **IMPORTANT:** Do NOT list utility software like "Discord", "Steam", "OBS", or "Nvidia GeForce Experience". I only want the actual game or application titles that are demanding on the hardware.

    {considerations_instruction}

    For each title you select, provide its official Minimum and Recommended system requirements.

    Your response MUST be a single, valid JSON object without any other text or markdown.
    The root key must be "discovered_applications".

    **CRITICAL RULE:** The "ram" and "storage_size" fields in the JSON MUST be **integers only**, representing the value in Gigabytes (GB). For example, "16 GB RAM" must be formatted as `"ram": 16`.

    JSON Structure Example:
    {{
        "discovered_applications": [
            {{
                "name": "Cyberpunk 2077",
                "source": "https://support.cdprojektred.com/en/cyberpunk/pc/sp-technical/issue/1558/system-requirements",
                "intensity_level": "high",
                "requirements": [
                    {{ "type": "minimum", "cpu": "Intel Core i7-6700", "gpu": "Nvidia GeForce GTX 1060 6GB", "ram": 12, "storage_size": 70, "storage_type": "SSD" }},
                    {{ "type": "recommended", "cpu": "Intel Core i7-12700", "gpu": "Nvidia GeForce RTX 2060 SUPER", "ram": 16, "storage_size": 70, "storage_type": "SSD" }}
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
