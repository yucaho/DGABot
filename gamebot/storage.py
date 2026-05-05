"""Persistence helpers for channel-specific sentiment files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gamebot.config import DATA_DIR


def _channel_file(channel_id: int) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / f"sentiments_{channel_id}.json"


def load_channel_sentiments(channel_id: int) -> list[dict[str, Any]]:
    path = _channel_file(channel_id)
    if not path.exists():
        return []

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_channel_sentiments(channel_id: int, rows: list[dict[str, Any]]) -> None:
    path = _channel_file(channel_id)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
