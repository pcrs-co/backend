from .ai_scraper import ask_gemini, ask_openai, query_all_ais
from .utils import clean_and_convert_to_int
from .ai_extractor import find_consensus_response, extract_requirements_from_response
from ..models import (
    Application,
    Activity,
    RequirementExtractionLog,
    ApplicationExtractionLog,
)
import json
from django.db import transaction


def discover_applications_for_activity(activity: Activity):
    """
    Uses AI to find a list of common applications for a given activity.
    """
    prompt = f"""
    List the top 5 most popular and essential software applications for the activity: "{activity.name}".
    Your response MUST be a single, valid JSON object with a single key "applications" which is an array of strings.
    Example: {{"applications": ["Application One", "Application Two", "Another App"]}}
    """

    # --- STRATEGY 1: TRY OPENAI ---
    print("Attempting to discover applications using OpenAI...")
    raw_response = ask_openai(prompt)
    method_used = "openai-discovery"

    # --- STRATEGY 2: FALLBACK TO GEMINI ---
    if not raw_response:
        print("OpenAI failed or returned no response. Falling back to Gemini...")
        raw_response = ask_gemini(prompt)
        method_used = "gemini-discovery-fallback"

    if not raw_response:
        print("Both OpenAI and Gemini failed to return a response.")
        ApplicationExtractionLog.objects.create(
            activity=activity,
            source_text=prompt,
            extracted_apps={"error": "No response from AIs"},
            method="failed-discovery",
            confidence=0.0,
        )
        return []

    try:
        data = json.loads(raw_response)
        app_names = data.get("applications", [])
        ApplicationExtractionLog.objects.create(
            activity=activity,
            source_text=prompt,
            extracted_apps={"applications": app_names},
            method=method_used,
            confidence=0.9,
        )
        print(f"Successfully discovered applications via {method_used}.")
        return app_names
    except (json.JSONDecodeError, AttributeError):
        print(f"Failed to parse JSON response from AI: {raw_response}")
        ApplicationExtractionLog.objects.create(
            activity=activity,
            source_text=raw_response,
            extracted_apps={"error": "JSON parse failed"},
            method=method_used,
            confidence=0.2,
        )
        return []


def discover_and_save_requirements(app_name: str, activity: Activity):
    """
    Main enrichment function. Finds system requirements for a single application,
    saves them to the database, and handles both creation and updates.
    """
    app = Application.objects.filter(name__iexact=app_name).first()

    prompt = f"""
    Give me the system requirements for the application: "{app_name}".
    Provide both "minimum" and "recommended" specifications.
    For storage, specify the recommended type (e.g., "SSD" or "HDD") if mentioned, and always provide size in GB. If the requirements say "SSD Recommended", set the storage_type to "SSD".
    Your response MUST be a single, valid JSON object. Do not add any text before or after the JSON.
    {{
      "name": "Corrected App Name",
      "source": "A valid URL to the official requirements page",
      "intensity_level": "low, medium, or high",
      "requirements": [
        {{"type": "minimum", "cpu": "Intel Core i5-6600K", "gpu": "NVIDIA GeForce GTX 970", "ram": 8, "storage_size": 50, "storage_type": "HDD"}},
        {{"type": "recommended", "cpu": "Intel Core i7-8700K", "gpu": "NVIDIA GeForce GTX 1080 Ti", "ram": 16, "storage_size": 50, "storage_type": "SSD"}}
      ]
    }}
    """

    raw_responses = query_all_ais(prompt)
    if not raw_responses:
        print(f"Could not get any AI response for '{app_name}'. Aborting.")
        return None

    try:
        structured = find_consensus_response(raw_responses)
    except ValueError as e:
        print(f"Could not get consensus for '{app_name}': {e}")
        return None

    with transaction.atomic():
        if not app:
            app = Application.objects.create(
                name=structured.get("name", app_name),
                source=structured.get("source"),
                intensity_level=structured.get("intensity_level", "medium"),
                activity=activity,
            )
        else:
            app.source = structured.get("source", app.source)
            app.intensity_level = structured.get("intensity_level", app.intensity_level)
            app.activity = activity  # Ensure it's linked to the current activity
            app.save()

        RequirementExtractionLog.objects.create(
            application=app,
            source_text="\n---\n".join(raw_responses),
            extracted_json=structured,
            method="multi-ai-consensus",
        )

        app.requirements.all().delete()
        for req in structured.get("requirements", []):
            # The model's .save() method will handle fetching scores automatically.
            # We just provide the raw data.
            app.requirements.create(
                type=req.get("type"),
                cpu=req.get("cpu"),
                gpu=req.get("gpu"),
                ram=clean_and_convert_to_int(req.get("ram", 0)),
                storage_size=clean_and_convert_to_int(req.get("storage_size", 0)),
                storage_type=req.get("storage_type", "Any"),
                notes=req.get("notes", ""),
            )
    return app
