import os
import openai
import google.generativeai as genai
import re
import json


try:
    client = openai.OpenAI()
except openai.OpenAIError as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

# --- Gemini Configuration (No changes needed) ---
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini API: {e}")


# --- Helper functions for each AI (Updated for new OpenAI syntax) ---
def ask_openai(prompt: str) -> str:
    if not client:
        print("OpenAI client not initialized. Skipping OpenAI call.")
        return ""

    try:
        system = "You are a helpful assistant that gives detailed application system requirements in a specific, structured JSON format."
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]

        # --- THIS IS THE KEY CHANGE ---
        # The new syntax uses client.chat.completions.create()
        response = client.chat.completions.create(
            model="gpt-4o",  # Using a more modern, JSON-friendly model
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"},  # Force JSON output
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return ""  # Return empty string on failure


def ask_gemini(prompt: str) -> str:
    """
    Queries Gemini and robustly extracts the JSON object from its response.
    """
    try:
        # It's better to instantiate the model each time or handle potential config errors.
        model = genai.GenerativeModel(
            "gemini-1.5-flash-latest"
        )  # Using a newer, faster model

        # We can also tell Gemini we expect JSON in the generation config
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json", temperature=0.1
        )

        response = model.generate_content(prompt, generation_config=generation_config)

        # Even with the mime_type hint, it's good to be safe.
        # Find the JSON block using a regular expression.
        # This looks for the first '{' to the last '}'
        json_match = re.search(r"\{.*\}", response.text, re.DOTALL)

        if json_match:
            json_string = json_match.group(0)
            # Final check to ensure it's valid JSON
            try:
                json.loads(json_string)
                return json_string
            except json.JSONDecodeError:
                print("Gemini response contained invalid JSON. Discarding.")
                return ""
        else:
            print("No valid JSON object found in Gemini's response.")
            return ""

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return ""


# --- Main function to call all AIs (No changes needed) ---
def query_all_ais(prompt: str) -> list[str]:
    """
    Queries all configured AI models with the same prompt.
    """
    # For production, consider using threading or asyncio for true parallelism
    responses = [
        ask_openai(prompt),
        ask_gemini(prompt),
    ]
    # Filter out any failed (empty) responses
    valid_responses = [resp for resp in responses if resp]
    print(f"Received {len(valid_responses)} valid responses from AIs.")
    return valid_responses
