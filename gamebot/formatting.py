"""Formatting utilities for sentiment categories and Discord output."""

from __future__ import annotations

from typing import Any

SENTIMENT_MAP = {
    "Buy": "Certified Banger",
    "Buy on Sale": "Wait for a Sale",
    "Don't Buy": "Hard Pass",
}

EMOJIS = {
    "Certified Banger": "🍆💦",
    "Wait for a Sale": "😬",
    "Hard Pass": "❌🗑️",
}

CATEGORIES = ["Certified Banger", "Wait for a Sale", "Hard Pass"]


def normalize_sentiment(raw: str) -> str:
    return SENTIMENT_MAP.get(raw.strip(), "Wait for a Sale")


def group_by_sentiment(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped = {cat: [] for cat in CATEGORIES}
    for row in rows:
        category = row.get("sentiment", "Wait for a Sale")
        if category not in grouped:
            grouped["Wait for a Sale"].append(row)
            continue
        grouped[category].append(row)
    return grouped


def render_game_line(row: dict[str, Any]) -> str:
    title = row.get("game", "Unknown Game")
    steam_url = row.get("steam_url")
    summary = row.get("summary", "No summary available.")
    sentiment = row.get("sentiment", "Wait for a Sale")
    emoji = EMOJIS.get(sentiment, "😬")

    linked_title = f"[{title}]({steam_url})" if steam_url else title
    first_line = f"{linked_title} - {summary} **{sentiment}** {emoji}"

    price = row.get("price", "N/A")
    review_percent = row.get("review_percent")
    review_count = row.get("review_count")

    if review_percent is not None and review_count is not None:
        second_line = f"💰 {price} — 💯 {review_percent}% positive ({_fmt_int(review_count)} reviews)"
    elif review_count is not None:
        second_line = f"💰 {price} — 💬 {_fmt_int(review_count)} reviews"
    else:
        second_line = f"💰 {price}"

    return f"{first_line}\n{second_line}"


def _fmt_int(value: Any) -> str:
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)
