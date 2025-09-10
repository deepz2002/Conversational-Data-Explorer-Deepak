# app/agent/llm.py
from __future__ import annotations
import os
from typing import Optional

from agno.models.google import Gemini


class LLMConfigError(RuntimeError):
    """Raised when required LLM configuration is missing or invalid."""


def get_llm(model_id: Optional[str] = None) -> Gemini:
    """
    Construct and return an Agno Gemini model instance.

    - Reads GOOGLE_API_KEY from the environment (required by Google's SDKs).
    - Model ID can be passed explicitly or via GEMINI_MODEL_ID env var.
      Defaults to a broadly-available fast model.

    Example:
        from app.agent.llm import get_llm
        llm = get_llm()  # Gemini(id=...)
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or not api_key.strip():
        raise LLMConfigError(
            "GOOGLE_API_KEY is not set. Add it to your environment or .env file."
        )

    resolved_model = (
        model_id
        or os.getenv("GEMINI_MODEL_ID")
        or "gemini-2.0-flash-001"  # safe default; change if your account prefers another
    )

    # Agno’s Gemini reads GOOGLE_API_KEY from the environment under the hood.
    # No direct dependency on `google-generativeai` here.
    return Gemini(id=resolved_model)