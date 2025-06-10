# ai_recommender/scraper.py
import requests
import re
import random
import logging
import json
from bs4 import BeautifulSoup
from django.utils.timezone import now
from django.conf import settings
from openai import OpenAI
import spacy

from .models import Activity, Application, ApplicationExtractionLog, ScrapingLog

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Simple predefined fallback
MOCK_APP_DB = {
    "Gaming": [
        {
            "name": "Cyberpunk 2077",
            "intensity_level": "high",
            "source": "https://example.com/cyberpunk",
        },
        {
            "name": "Valorant",
            "intensity_level": "medium",
            "source": "https://example.com/valorant",
        },
        {
            "name": "Minecraft",
            "intensity_level": "low",
            "source": "https://example.com/minecraft",
        },
    ],
    "Video Editing": [
        {
            "name": "Adobe Premiere Pro",
            "intensity_level": "high",
            "source": "https://example.com/premiere",
        },
        {
            "name": "DaVinci Resolve",
            "intensity_level": "high",
            "source": "https://example.com/davinci",
        },
    ],
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}


def scrape_google_search_results(activity_name):
    """
    Scrape Google search results to extract text blocks for regex/spaCy-based app extraction.
    """
    search_query = f"best software for {activity_name} 2025"
    search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text_blocks = " ".join(p.get_text() for p in soup.find_all("p"))
        logger.info(f"Fetched search result text for '{activity_name}'.")
        return text_blocks
    except Exception as e:
        logger.error(f"Failed to scrape search results for '{activity_name}': {e}")
        return ""


def regex_based_extraction(text):
    pattern = r"\b([A-Z][a-zA-Z0-9\s]{2,30})\b"
    matches = re.findall(pattern, text)
    return list(set(matches))


def spacy_based_extraction(text):
    doc = nlp(text)
    return list(set(ent.text for ent in doc.ents if ent.label_ == "PRODUCT"))


def ai_based_extraction(activity_name):
    prompt = (
        f"List 5 popular software applications for '{activity_name}' in 2025. "
        f"For each, give: name - intensity level (low/medium/high) - source URL. "
        f"Return as JSON array like: "
        f"[{{'name': 'App', 'intensity_level': 'high', 'source': 'https://example.com'}}]"
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant for extracting software application data.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        response_text = completion.choices[0].message.content.strip()
        apps = json.loads(response_text)
        logger.info(f"AI extraction returned {len(apps)} apps for '{activity_name}'.")
        return apps
    except Exception as e:
        logger.warning(f"AI extraction failed for '{activity_name}': {e}")
        return []


def scrape_applications_for_activity(activity_name):
    # 1️⃣ Web scraping & text extraction
    text_blocks = scrape_google_search_results(activity_name)

    # 2️⃣ Regex-based extraction
    regex_apps = regex_based_extraction(text_blocks)

    # 3️⃣ spaCy-based extraction
    spacy_apps = spacy_based_extraction(text_blocks)

    # 4️⃣ AI fallback
    ai_apps = ai_based_extraction(activity_name)

    # 5️⃣ Build final list of applications
    all_apps = set(regex_apps + spacy_apps)
    extracted_apps = []

    # If AI returned structured data, prefer that
    if ai_apps:
        for app_data in ai_apps:
            extracted_apps.append(
                {
                    "name": app_data.get("name"),
                    "intensity_level": app_data.get(
                        "intensity_level", "medium"
                    ).lower(),
                    "source": app_data.get("source"),
                }
            )
        confidence = 0.9
        source = "ai_search"
    elif all_apps:
        for name in all_apps:
            extracted_apps.append(
                {
                    "name": name.strip(),
                    "intensity_level": random.choice(["low", "medium", "high"]),
                    "source": f"https://www.google.com/search?q={name.replace(' ', '+')}",
                }
            )
        confidence = 0.7
        source = "regex_spacy"
    else:
        # Final fallback to MOCK DB
        fallback_apps = MOCK_APP_DB.get(activity_name, [])
        extracted_apps.extend(fallback_apps)
        confidence = 0.5
        source = "mock"

    # 6️⃣ Save extraction log
    activity, _ = Activity.objects.get_or_create(name=activity_name)
    ApplicationExtractionLog.objects.create(
        activity=activity,
        source_text=text_blocks[:1000],
        extracted_apps=[app["name"] for app in extracted_apps],
        timestamp=now(),
        method="regex+spacy+openai",
        confidence=confidence,
        reviewed=False,
    )

    # 7️⃣ Save Application records
    for app_data in extracted_apps:
        app, _ = Application.objects.get_or_create(name=app_data["name"])
        app.activity = activity
        app.intensity_level = app_data.get("intensity_level", "medium")
        app.source = app_data.get("source")
        app.save()

    # 8️⃣ Save scraping log
    ScrapingLog.objects.create(
        activity=activity,
        source=source,
        app_count=len(extracted_apps),
        timestamp=now(),
    )

    logger.info(
        f"Completed extraction for '{activity_name}' with {len(extracted_apps)} apps (source: {source}, confidence: {confidence})."
    )


def run_extraction_for_all_activities():
    activities = Activity.objects.filter(applications__isnull=True)
    logger.info(f"Found {activities.count()} activities without applications.")
    for activity in activities:
        scrape_applications_for_activity(activity.name)
