"""
LLM abstraction layer.

Tries Groq (llama-3.3-70b-versatile) first, falls back to Google Gemini
(gemini-1.5-flash) on any failure.  Exposes a single `call_llm()` function
so callers never need to care which backend answered.
"""

import os
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class LLMError(Exception):
    """Raised when every LLM backend fails."""


def _call_groq(system_prompt: str, user_prompt: str) -> str:
    """Attempt a completion via Groq."""
    from groq import Groq  # lazy import to avoid hard crash if not installed

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=4096,
    )
    return response.choices[0].message.content


_GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    """Attempt a completion via Google Gemini (tries models in order)."""
    from google import genai  # google-genai package (v1 API)

    client = genai.Client(api_key=GEMINI_API_KEY)
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    last_exc: Exception = Exception("No Gemini models attempted")
    for model_name in _GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
            )
            logger.info("[LLM] Gemini responded using model=%s", model_name)
            return response.text
        except Exception as exc:
            logger.warning("[LLM] Gemini model %s failed: %s", model_name, exc)
            last_exc = exc

    raise last_exc


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Send a prompt to an LLM and return the text response.

    Tries Groq first; on *any* exception falls back to Gemini.
    If both fail, raises ``LLMError``.
    """
    try:
        logger.info("[LLM] Using Groq")
        return _call_groq(system_prompt, user_prompt)
    except Exception as exc:
        logger.warning("[LLM] Groq failed (%s), falling back to Gemini", exc)

    try:
        logger.info("[LLM] Using Gemini")
        return _call_gemini(system_prompt, user_prompt)
    except Exception as exc:
        logger.error("[LLM] Gemini also failed: %s", exc)
        raise LLMError(
            "All LLM backends failed. Check API keys and quotas."
        ) from exc
