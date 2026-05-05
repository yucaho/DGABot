"""Configuration loading for GameBot."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env if present.
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Optional model override for experimentation.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# Bot settings.
MESSAGE_FETCH_LIMIT = int(os.getenv("MESSAGE_FETCH_LIMIT", "200"))
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))


def validate_config() -> None:
    """Raise a friendly error if required environment variables are missing."""
    missing: list[str] = []
    if not DISCORD_TOKEN:
        missing.append("DISCORD_TOKEN")
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")

    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing required environment variables: {joined}. "
            "Create a .env file (see .env.example) and try again."
        )
