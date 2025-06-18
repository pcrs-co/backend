import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


def ask_openai(prompt: str) -> str:
    system = "You are a helpful assistant that gives detailed application system requirements in structured JSON format."
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=messages, temperature=0.2  # or gpt-3.5-turbo
    )
    return response["choices"][0]["message"]["content"]
