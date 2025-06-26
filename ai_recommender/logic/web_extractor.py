# ai_recommender/logic/web_extractor.py

import requests
from bs4 import BeautifulSoup
from googlesearch import search
from .ai_scraper import ask_openai, ask_gemini
import json


def get_page_content(url: str) -> str:
    """Fetches and cleans the text content of a given URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text, strip leading/trailing whitespace, and join with newlines
        text = " ".join(soup.stripped_strings)

        # Limit the text to a reasonable size to not overwhelm the AI
        max_chars = 15000
        return text[:max_chars]

    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None


def find_requirements_from_web(app_name: str) -> dict | None:
    """
    Searches the web for an application's system requirements, scrapes the page,
    and uses an AI to extract the structured data.
    """
    print(f"--- Starting Web Search for '{app_name}' ---")
    query = f'"{app_name}" official system requirements'

    try:
        # Find the top search result
        search_results = list(search(query, num_results=3, lang="en"))
        if not search_results:
            print(f"No search results found for '{app_name}'.")
            return None

        # Try the top few URLs
        for url in search_results:
            print(f"Scraping URL: {url}")
            page_content = get_page_content(url)

            if not page_content:
                continue  # Try the next URL if scraping failed

            # Now, use a powerful AI to extract information from the scraped text
            extraction_prompt = f"""
            From the following raw text scraped from a website, extract the system requirements for the application "{app_name}".
            Your response MUST be a single, valid JSON object with the exact structure below. Do not add any text before or after the JSON.
            If you cannot find the information, use null for the values.

            Desired JSON Structure:
            {{
              "name": "Corrected App Name",
              "source": "{url}",
              "intensity_level": "low, medium, or high",
              "requirements": [
                {{"type": "minimum", "cpu": "Intel Core i5-6600K", "gpu": "NVIDIA GeForce GTX 970", "ram": 8, "storage": 50}},
                {{"type": "recommended", "cpu": "Intel Core i7-8700K", "gpu": "NVIDIA GeForce GTX 1080 Ti", "ram": 16, "storage": 50}}
              ]
            }}

            --- RAW TEXT ---
            {page_content}
            """

            # GPT-4o is generally best for this kind of complex extraction from messy text
            raw_response = ask_openai(extraction_prompt)

            if raw_response:
                try:
                    structured_data = json.loads(raw_response)
                    # Basic validation
                    if (
                        "requirements" in structured_data
                        and len(structured_data["requirements"]) > 0
                    ):
                        print(
                            f"Successfully extracted requirements for '{app_name}' from the web."
                        )
                        return structured_data
                except json.JSONDecodeError:
                    print(
                        f"Failed to parse JSON from AI response for {app_name}. Trying next source."
                    )
                    continue

        print(
            f"Could not extract requirements from the top 3 web sources for '{app_name}'."
        )
        return None

    except Exception as e:
        print(f"An error occurred during web search for '{app_name}': {e}")
        return None
