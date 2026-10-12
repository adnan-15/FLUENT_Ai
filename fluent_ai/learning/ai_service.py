
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:1b"

SYSTEM_INSTRUCTIONS = """
You are Fluent AI, an English-learning assistant.

Your responsibilities:
- Answer the user's actual question.
- Handle normal conversation naturally.
- Correct grammar when useful and explain mistakes simply.
- Help with vocabulary and conversational English.
- Give pronunciation tips when requested.
- Provide short, practical examples when useful.
- Keep answers concise and suitable for speaking aloud.
- Do not give unrelated lessons.
- Do not correct every sentence unless correction is useful or requested.
"""


def generate_ai_response(message):
    """
    Generate an AI response using the local Ollama model.

    Args:
        message (str): The user's message.

    Returns:
        str: The AI-generated response.

    Raises:
        ValueError: If the message is empty or invalid.
        RuntimeError: If Ollama fails or returns an invalid response.
    """

    if not isinstance(message, str) or not message.strip():
        raise ValueError("Please provide a valid message.")

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": message.strip(),
            },
        ],
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": 0.3,
            "num_predict": 150,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=(5, 120),
        )

        response.raise_for_status()

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise RuntimeError(
                "Ollama returned an invalid JSON response."
            ) from exc

        answer = data.get("message", {}).get("content", "")

        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError(
                "The AI returned an empty or invalid response."
            )

        return answer.strip()

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "The AI took too long to respond. Please try again."
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure Ollama is running "
            "and the model is available."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else "unknown"
        )

        raise RuntimeError(
            f"Ollama API error ({status_code}). "
            "Check the Ollama server and model configuration."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "An error occurred while communicating with Ollama."
        ) from exc
