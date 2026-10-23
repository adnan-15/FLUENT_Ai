
import os
import requests

OLLAMA_URL = "https://ollama.com/api/chat"
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
MODEL_NAME = "gemma4:31b"

SYSTEM_INSTRUCTIONS = """
You are Fluent AI, an English-learning assistant.
- Answer the user's actual question.
- Correct grammar when useful and explain mistakes simply.
- Help with vocabulary and conversational English.
- Give pronunciation tips when requested.
- Keep answers concise and suitable for speaking aloud.
- Do not give unrelated lessons.
- Do not correct every sentence unless useful or requested.
"""


def generate_ai_response(message):
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Please provide a valid message.")

    if not OLLAMA_API_KEY:
        raise RuntimeError("OLLAMA_API_KEY is not configured.")

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": message.strip()},
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 150,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            headers={
                "Authorization": f"Bearer {OLLAMA_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=(5, 120),
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("message", {}).get("content", "")

        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("The AI returned an empty response.")

        return answer.strip()

    except requests.exceptions.Timeout as exc:
        raise RuntimeError("The AI took too long to respond.") from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"Ollama API error ({exc.response.status_code}). "
            "Check your API key and model availability."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError("Could not connect to Ollama Cloud.") from exc
