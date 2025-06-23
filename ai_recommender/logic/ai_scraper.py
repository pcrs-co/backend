import os
import openai
import google.generativeai as genai
import anthropic

# --- API Key Configuration ---
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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


def ask_claude(prompt: str) -> str:
    try:
        system = "You are a helpful assistant. Your only task is to respond with a single, valid JSON object containing detailed application system requirements, based on the user's request. Do not include any text before or after the JSON object."
        message = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",  # Haiku is fast and cheap, good for this
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Claude: {e}")
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
        ask_claude(prompt),
    ]
    # Filter out any failed (empty) responses
    return [resp for resp in responses if resp]
