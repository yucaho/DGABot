"""OpenAI integration for analyzing Discord messages."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from gamebot.config import OPENAI_API_KEY, OPENAI_MODEL
from gamebot.prompts import ANALYZE_MESSAGES_PROMPT


class OpenAIAnalyzer:
    """Wraps OpenAI calls and response parsing for game sentiment analysis."""

    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def analyze_messages(self, messages_text: str) -> list[dict[str, Any]]:
        """Analyze a message transcript and return normalized game sentiment rows."""
        prompt = ANALYZE_MESSAGES_PROMPT.format(messages=messages_text)

        response = self.client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0.2,
        )

        raw_text = response.output_text or "[]"
        cleaned = _strip_markdown_fences(raw_text)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "OpenAI returned non-JSON content. Try again or reduce message noise."
            ) from exc

        if not isinstance(parsed, list):
            raise ValueError("OpenAI response JSON must be a list.")

        return [item for item in parsed if isinstance(item, dict)]


def _strip_markdown_fences(text: str) -> str:
    """Strip optional markdown code fences from model output."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        # Drop first fence line
        lines = lines[1:]
        # Drop trailing fence line if present
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped
