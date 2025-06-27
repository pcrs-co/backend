# ai_recommender/logic/ai_scraper.py

import os
import openai
import google.generativeai as genai
import time
import json

# --- Client Initialization ---
# This part remains the same. It's good practice.
try:
    client = openai.OpenAI()
except openai.OpenAIError as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini API: {e}")


# --- Private Helper Functions ---


def _ask_gemini(prompt: str) -> str:
    """
    A private helper to query Gemini. Returns an empty string on failure.
    """
    try:
        print("Attempting to query Gemini model: gemini-1.5-flash-latest...")
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json", temperature=0.1
        )
        response = model.generate_content(prompt, generation_config=generation_config)

        # The API with `application/json` should return a clean JSON string.
        # We perform a basic check to ensure it's not empty and looks like JSON.
        if response.text and response.text.strip().startswith("{"):
            print("Successfully received response from Gemini.")
            return response.text
        else:
            print(f"Gemini returned an invalid or empty response: {response.text}")
            return ""
    except Exception as e:
        # The API library will print its own specific error (e.g., 429 Quota Exceeded)
        print(f"An error occurred while calling Gemini API: {e}")
        return ""


def _ask_openai(prompt: str) -> str:
    """
    A private helper that tries a chain of OpenAI models, returning the first
    successful response. Returns an empty string on failure.
    """
    if not client:
        print("OpenAI client not initialized. Skipping all OpenAI calls.")
        return ""

    # Chain of models to try, from best/newest to most common.
    models_to_try = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

    for model_name in models_to_try:
        try:
            print(f"Attempting to query OpenAI model: {model_name}...")
            system_prompt = "You are a helpful assistant that gives detailed application system requirements in a specific, structured JSON format. Your entire response must be ONLY the JSON object, with no other text."
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if content:
                print(f"Successfully received response from OpenAI model: {model_name}")
                return content
        except Exception as e:
            # The openai library often prints useful info in the exception.
            print(f"Error calling OpenAI model '{model_name}': {e}")
            # Wait a moment before trying the next model in the chain.
            time.sleep(1)
            continue  # Move to the next model

    print("All OpenAI models failed or returned no response.")
    return ""


# --- The ONLY Public Function Exposed to the Rest of the Application ---


def get_ai_response(prompt: str) -> str:
    """
    Gets a structured JSON response from an AI service.

    It follows a specific fallback strategy:
    1. Try Gemini first.
    2. If Gemini fails, fall back to the OpenAI model chain (gpt-4o -> gpt-4-turbo -> gpt-3.5-turbo).

    Returns:
        A string containing the AI's JSON response, or an empty string if all services fail.
    """
    # --- STRATEGY 1: TRY GEMINI ---
    gemini_response = _ask_gemini(prompt)
    if gemini_response:
        return gemini_response

    # --- STRATEGY 2: FALLBACK TO OPENAI ---
    print("\nGemini failed. Falling back to the OpenAI model chain...")
    time.sleep(1)  # A small pause before switching services
    openai_response = _ask_openai(prompt)
    if openai_response:
        return openai_response

    # --- FINAL FAILURE ---
    print(
        "\nCRITICAL: All AI services (Gemini and OpenAI) failed to provide a response."
    )
    return ""
