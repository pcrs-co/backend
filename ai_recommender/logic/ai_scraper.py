import os
import openai
import google.generativeai as genai

# --- API Key Configuration ---
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Helper functions for each AI ---


def ask_openai(prompt: str) -> str:
    try:
        system = "You are a helpful assistant that gives detailed application system requirements in a specific, structured JSON format."
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",  # Using a more modern, JSON-friendly model
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"},  # Force JSON output
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return ""  # Return empty string on failure


def ask_gemini(prompt: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        # Gemini's output might have markdown ```json ... ```, so we clean it.
        cleaned_response = (
            response.text.replace("```json", "").replace("```", "").strip()
        )
        return cleaned_response
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return ""


# --- Main function to call all AIs ---


def query_all_ais(prompt: str) -> list[str]:
    """
    Queries all configured AI models with the same prompt in parallel.
    (Note: For true parallelism, you would use threading or asyncio,
    but for simplicity, we'll do it sequentially here.)
    """
    responses = [
        ask_openai(prompt),
        ask_gemini(prompt),
    ]
    # Filter out any failed (empty) responses
    return [resp for resp in responses if resp]
