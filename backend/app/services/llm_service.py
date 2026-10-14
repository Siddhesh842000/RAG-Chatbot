import threading

import groq
from groq import Groq

from app.config import settings
from app.utils.prompts import (
    NOT_FOUND_MESSAGE,
    SYSTEM_PROMPT,
    build_context,
    build_user_prompt,
)


class LLMError(Exception):
    """Something went wrong while talking to the LLM.

    status_code is the HTTP status the API route should return later.
    """

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# The Groq client is created one time and reused.
_client: Groq | None = None
_lock = threading.Lock()


def _get_client() -> Groq:
    global _client

    key = settings.GROQ_API_KEY
    if not key or key == "your_key_here":
        raise LLMError("GROQ_API_KEY is not set on the server.", 500)

    if _client is None:
        with _lock:
            if _client is None:
                _client = Groq(
                    api_key=key,
                    timeout=settings.LLM_TIMEOUT_SECONDS,
                    max_retries=2,  # retry short network problems automatically
                )
    return _client


def reset_client() -> None:
    """Forget the client. Used by tests after changing the key."""
    global _client
    _client = None


def chat(messages: list[dict]) -> str:
    """Send messages to GPT-OSS 120B on Groq and return the answer text."""
    client = _get_client()

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,  # low = stable, factual answers
            max_completion_tokens=settings.LLM_MAX_TOKENS,
            reasoning_effort=settings.LLM_REASONING_EFFORT,
        )
    except groq.AuthenticationError as exc:
        raise LLMError("The Groq API key on the server is invalid.", 500) from exc
    except groq.RateLimitError as exc:
        raise LLMError(
            "The AI service is busy right now (rate limit). Please try again in a minute.", 429
        ) from exc
    except groq.NotFoundError as exc:
        raise LLMError("The AI model was not found. Check GROQ_MODEL on the server.", 500) from exc
    except groq.APITimeoutError as exc:
        raise LLMError("The AI service took too long to respond. Please try again.", 504) from exc
    except groq.APIConnectionError as exc:
        raise LLMError("Could not connect to the AI service. Please try again.", 503) from exc
    except groq.APIStatusError as exc:
        raise LLMError(f"The AI service returned an error (status {exc.status_code}).", 502) from exc

    answer = (response.choices[0].message.content or "").strip()
    if not answer:
        raise LLMError("The AI model returned an empty answer. Please try again.", 502)
    return answer


def generate_answer(question: str, chunks: list[dict]) -> str:
    """Answer a question using only the retrieved chunks."""
    # Nothing was retrieved, so there is nothing to answer from.
    # We skip the LLM call completely.
    if not chunks:
        return NOT_FOUND_MESSAGE

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(build_context(chunks), question)},
    ]
    return chat(messages)
