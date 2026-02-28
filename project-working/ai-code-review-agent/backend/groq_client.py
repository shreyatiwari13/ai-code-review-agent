import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def call_groq_system(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    """
    Calls Groq OpenAI-compatible chat API and returns raw model output string.
    """

    # ✅ FIX 1: Raise error instead of returning fake JSON
    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY in .env file")

    url = f"{GROQ_API_URL}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "response_format": {"type": "json_object"}  # ✅ Force strict JSON
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        # ✅ Validate structure before returning
        if "choices" not in data or not data["choices"]:
            raise RuntimeError("Invalid response from Groq API")

        return data["choices"][0]["message"]["content"]

    # ✅ FIX 2: Raise errors instead of returning JSON
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Groq API request failed: {str(e)}")

    except Exception as e:
        raise RuntimeError(f"Unexpected Groq error: {str(e)}")