from ..models import Application, ApplicationSystemRequirement, Activity
from .ai_scraper import ask_openai
from .ai_extractor import extract_requirements_from_response
from .utils import get_cpu_score, get_gpu_score


def enrich_application(application_name, activity_name=None):
    # Check if app exists
    app = Application.objects.filter(name__iexact=application_name).first()
    if app:
        return app  # No need to enrich again

    # Prompt AI
    prompt = f"""
Give me the system requirements for the application: {application_name}. 
Include both minimum and recommended specs, with CPU, GPU, RAM (in GB), Storage (in GB), and a source URL.
Structure your answer in JSON like this:
{{
  "name": "App Name",
  "source": "...",
  "intensity_level": "low/medium/high",
  "requirements": [
    {{
      "type": "minimum",
      "cpu": "...",
      "gpu": "...",
      "ram": 8,
      "storage": 10
    }},
    {{
      "type": "recommended",
      "cpu": "...",
      "gpu": "...",
      "ram": 16,
      "storage": 20
    }}
  ]
}}
"""
    raw_response = ask_openai(prompt)
    structured = extract_requirements_from_response(raw_response)

    # Get or create the Activity
    activity = None
    if activity_name:
        activity, _ = Activity.objects.get_or_create(
            name__iexact=activity_name, defaults={"name": activity_name}
        )
    elif Activity.objects.exists():
        activity = Activity.objects.first()

    # Save the Application
    app = Application.objects.create(
        name=structured["name"],
        source=structured.get("source"),
        intensity_level=structured.get("intensity_level", "medium"),
        activity=activity,
    )

    # Save each Requirement with benchmark scores
    for req in structured["requirements"]:
        cpu = req.get("cpu")
        gpu = req.get("gpu")

        ApplicationSystemRequirement.objects.create(
            application=app,
            type=req["type"],
            cpu=cpu,
            gpu=gpu,
            cpu_score=get_cpu_score(cpu),
            gpu_score=get_gpu_score(gpu),
            ram=req.get("ram", 4),
            storage=req.get("storage", 10),
            notes=req.get("notes", ""),
        )

    return app
