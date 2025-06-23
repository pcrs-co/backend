# ai_recommender/logic/enrich_app_data.py

from ..models import Application, ApplicationSystemRequirement, Activity
from .ai_scraper import query_all_ais # Updated import
from .ai_extractor import find_consensus_response # Updated import
from .utils import get_cpu_score, get_gpu_score

def enrich_application(application_name, activity_name=None):
    app = Application.objects.filter(name__iexact=application_name).first()
    if app:
        return app  # No need to enrich again

    # --- KEY CHANGE: Use the multi-AI workflow ---
    prompt = f"""
Give me the system requirements for the application: "{application_name}". 
Provide both "minimum" and "recommended" specifications.
Your response MUST be a single, valid JSON object with the following structure. Do not add any text before or after the JSON.
{{
  "name": "Corrected App Name",
  "source": "A valid URL to the official requirements page",
  "intensity_level": "low, medium, or high",
  "requirements": [
    {{
      "type": "minimum", "cpu": "e.g., Intel Core i5-6600K", "gpu": "e.g., NVIDIA GeForce GTX 970", "ram": 8, "storage": 50
    }},
    {{
      "type": "recommended", "cpu": "e.g., Intel Core i7-8700K", "gpu": "e.g., NVIDIA GeForce GTX 1080 Ti", "ram": 16, "storage": 50
    }}
  ]
}}
"""
    # Query all AIs and get a list of raw string responses
    raw_responses = query_all_ais(prompt)
    
    # Find the best response through consensus
    try:
        structured = find_consensus_response(raw_responses)
    except ValueError as e:
        print(f"Could not enrich application '{application_name}': {e}")
        return None # Or raise an exception to signal failure
    # --- END OF KEY CHANGE ---

    activity = None
    if activity_name:
        activity, _ = Activity.objects.get_or_create(
            name__iexact=activity_name, defaults={"name": activity_name}
        )
    elif Activity.objects.exists():
        activity = Activity.objects.first()

    app = Application.objects.create(
        name=structured.get("name", application_name), # Use AI's corrected name
        source=structured.get("source"),
        intensity_level=structured.get("intensity_level", "medium"),
        activity=activity,
    )

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
            notes=req.get("notes", ""),
        )

    return app