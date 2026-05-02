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


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    """Attempt a completion via Google Gemini."""
    import google.generativeai as genai  # lazy import

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt,
    )
    response = model.generate_content(user_prompt)
    return response.text


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
