# ai_recommender/extractor/extractor.py
import requests
from bs4 import BeautifulSoup
import logging
from django.utils.timezone import now
from django.conf import settings
from openai import OpenAI
from ..models import Application, ApplicationSystemRequirement, RequirementExtractionLog
from .regex_parser import parse_system_requirements
from .extractor_utils import compare_extractions, log_differences  # NEW

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def extract_requirements_for_application(app):
    try:
        response = requests.get(app.source, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract possible relevant text
        candidates = soup.find_all(string=lambda t: "requirement" in t.lower())
        relevant_text = " ".join([c.strip() for c in candidates if len(c.strip()) > 30])

        # Regex extraction
        parsed_regex = parse_system_requirements(relevant_text)
        logger.debug(f"Regex extraction for '{app.name}': {parsed_regex}")

        has_useful_data = any(
            any([r.get("cpu"), r.get("gpu"), r.get("ram"), r.get("storage")])
            for r in parsed_regex
        )

        # LLM extraction for comparison
        prompt = (
            "Extract system requirements (minimum and recommended) from the following text. "
            "Return JSON format with fields: type (minimum/recommended), cpu, gpu, ram (GB), "
            "storage (GB), notes. Here is the text:\n\n"
            f"{relevant_text}"
        )

        llm_response = None
        parsed_llm = []
        try:
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a system requirements extraction assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            llm_response = completion.choices[0].message.content
            import json

            parsed_llm = json.loads(llm_response)
            logger.debug(f"LLM extraction for '{app.name}': {parsed_llm}")
        except Exception as llm_err:
            logger.error(f"OpenAI extraction failed for '{app.name}': {llm_err}")

        # Compare regex vs LLM extraction
        diffs = compare_extractions(parsed_regex, parsed_llm)
        log_differences(app.name, diffs)

        # Decide final extraction data
        if has_useful_data:
            final_data = parsed_regex
            method = "regex"
            confidence = 0.5
        else:
            final_data = parsed_llm
            method = "openai"
            confidence = 0.9

        # Save extraction log
        log = RequirementExtractionLog.objects.create(
            application=app,
            source_text=relevant_text,
            extracted_json=final_data,
            timestamp=now(),
            method=method,
            confidence=confidence,
            reviewed=False,
        )

        # Save structured requirements
        for req in final_data:
            if any(
                [req.get("cpu"), req.get("gpu"), req.get("ram"), req.get("storage")]
            ):
                ApplicationSystemRequirement.objects.create(
                    application=app,
                    type=req.get("type", "minimum"),
                    cpu=req.get("cpu"),
                    gpu=req.get("gpu"),
                    ram=req.get("ram"),
                    storage=req.get("storage"),
                    notes=req.get("notes", f"Extracted via log {log.id}"),
                )

        logger.info(f"Extraction completed for '{app.name}' using {method} method.")
    except Exception as e:
        logger.exception(f"Failed to extract requirements for '{app.name}': {e}")


def run_extraction_for_all_apps():
    apps = Application.objects.filter(applicationrequirements__isnull=True)
    logger.info(f"Found {apps.count()} applications missing requirements.")
    for app in apps:
        extract_requirements_for_application(app)
