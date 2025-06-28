# ai_recommender/logic/web_extractor.py

import requests
from bs4 import BeautifulSoup
from googlesearch import search
from .ai_scraper import _ask_openai, _ask_gemini
import json


def get_structured_component(generic_name: str, component_type: str) -> dict | None:
    """
    Uses an AI to convert a generic component name like "2 GHz Dual Core Processor"
    into a structured dictionary and then finds the best match in the benchmark DB.
    """
    if not generic_name or "none" in generic_name.lower():
        return None

    print(f"--- Structuring generic name: '{generic_name}' ---")

    prompt = f"""
    Analyze the following generic computer component description: "{generic_name}".
    Convert it into a structured JSON object with the following keys: "brand" (e.g., "Intel", "AMD", "NVIDIA"), "cores" (integer, null if not specified), "clock_speed_ghz" (float, null if not specified).
    If a key's information is not present, use null. Your entire response must be ONLY the JSON object.

    Example for "2 GHz Dual Core Processor":
    {{
        "brand": null,
        "cores": 2,
        "clock_speed_ghz": 2.0
    }}

    Example for "Intel Core i5":
    {{
        "brand": "Intel",
        "cores": null,
        "clock_speed_ghz": null
    }}
    """
    # Use the fastest/cheapest model for this simple task
    response_text = _ask_gemini(prompt) or _ask_openai(prompt)
    if not response_text:
        print(f"AI failed to structure the component name '{generic_name}'.")
        return None

    try:
        attrs = json.loads(response_text)
    except json.JSONDecodeError:
        print(f"Failed to parse AI response for structuring: {response_text}")
        return None
    from ..models import CPUBenchmark, GPUBenchmark, find_best_benchmark_match

    # Now, use these attributes to query the database
    Model = CPUBenchmark if component_type == "cpu" else GPUBenchmark
    qs = Model.objects.all()

    # Build a query based on the structured attributes
    query_filters = Q()
    name_field = "cpu" if component_type == "cpu" else "gpu"

    if attrs.get("brand"):
        query_filters &= Q(**{f"{name_field}__icontains": attrs["brand"]})

    if attrs.get("clock_speed_ghz"):
        # Find clock speeds within a +/- 10% range
        speed = attrs["clock_speed_ghz"]
        # This regex looks for patterns like 2.0GHz, 2.00 GHz, @ 2.0Ghz etc.
        qs = qs.filter(**{f"{name_field}__iregex": rf"@{speed:.1f}\d? *GHz"})

    # This is a simplification. A more complex query could be built for cores.
    # For now, we'll rely on brand and clock speed.

    candidates = qs.filter(query_filters).order_by("score")

    if not candidates.exists():
        print(f"No benchmark candidates found for structured attrs: {attrs}")
        # Fallback to your original fuzzy matching as a last resort
        return find_best_benchmark_match(generic_name, Model)

    # From the candidates, pick one. The lowest-scoring one that meets the spec is a safe bet.
    best_match = candidates.first()
    print(
        f"Structured match found for '{generic_name}': '{getattr(best_match, name_field)}'"
    )
    return best_match


def find_requirements_from_web(app_name: str) -> dict | None:
    """
    Searches the web, scrapes content, and uses an AI consensus model
    to extract the most reliable structured data.
    """
    print(f"--- Starting Web Search for '{app_name}' ---")
    query = f'"{app_name}" official system requirements'

    try:
        search_results = list(search(query, num_results=3, lang="en"))
        if not search_results:
            return None

        # --- NEW: Collect multiple AI responses ---
        all_ai_responses = []

        for url in search_results:
            print(f"Scraping URL: {url}")
            page_content = get_page_content(url)
            if not page_content:
                continue

            extraction_prompt = f"""... (your prompt remains the same) ..."""

            # Get responses from multiple sources if possible
            gemini_resp = ask_gemini(extraction_prompt)
            if gemini_resp:
                all_ai_responses.append(gemini_resp)

            openai_resp = ask_openai(extraction_prompt)
            if openai_resp:
                all_ai_responses.append(openai_resp)

        if not all_ai_responses:
            print(f"No AI responses generated from any web source for '{app_name}'.")
            return None

        # --- NEW: Find the consensus response ---
        return find_consensus_response(all_ai_responses)

    except Exception as e:
        print(f"An error occurred during web search for '{app_name}': {e}")
        return None


def find_consensus_response(responses: list[str]) -> dict | None:
    """
    Parses multiple JSON string responses from an AI and finds the most
    complete and plausible one to be the "winner".
    """
    parsed_data = []
    for resp in responses:
        try:
            # Clean up potential markdown code blocks
            clean_resp = resp.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_resp)
            # Basic validation: must have a name and requirements list
            if data.get("name") and isinstance(data.get("requirements"), list):
                parsed_data.append(data)
        except (json.JSONDecodeError, AttributeError):
            continue  # Ignore responses that aren't valid JSON

    if not parsed_data:
        return None

    # Score each response based on how "complete" it is.
    # A more complete response is more likely to be correct.
    def calculate_score(item):
        score = 0
        if item.get("name"):
            score += 1
        if item.get("source"):
            score += 1
        if item.get("intensity_level"):
            score += 1
        if len(item.get("requirements", [])) == 2:
            score += 5  # High value on both min/rec
        for req in item.get("requirements", []):
            if req.get("cpu"):
                score += 2
            if req.get("gpu"):
                score += 2
            if req.get("ram"):
                score += 2
        return score

    # Return the response with the highest completeness score
    best_response = max(parsed_data, key=calculate_score)
    print(
        f"Consensus found. Choosing response with best score for '{best_response.get('name')}'."
    )
    return best_response


# def get_page_content(url: str) -> str:
#     """Fetches and cleans the text content of a given URL."""
#     try:
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         }
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()  # Raise an exception for bad status codes

#         soup = BeautifulSoup(response.text, "html.parser")

#         # Remove script and style elements
#         for script_or_style in soup(["script", "style"]):
#             script_or_style.decompose()

#         # Get text, strip leading/trailing whitespace, and join with newlines
#         text = " ".join(soup.stripped_strings)

#         # Limit the text to a reasonable size to not overwhelm the AI
#         max_chars = 15000
#         return text[:max_chars]

#     except requests.RequestException as e:
#         print(f"Error fetching URL {url}: {e}")
#         return None
