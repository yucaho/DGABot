"""Steam API client using aiohttp only (no blocking requests)."""

from __future__ import annotations

from typing import Any

import aiohttp

SEARCH_URL = "https://store.steampowered.com/api/storesearch/"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"


class SteamClient:
    """Fetches Steam metadata for game names."""

    async def fetch_game(self, game_title: str) -> dict[str, Any] | None:
        """Search steam by title and enrich with app details."""
        search_data = await self._search(game_title)
        if not search_data:
            return None

        app_id = search_data.get("id")
        if not app_id:
            return None

        details = await self._app_details(str(app_id))
        if not details:
            return None

        data = details.get("data", {})
        price = _extract_price(data)
        review_count = data.get("recommendations", {}).get("total")

        return {
            "app_id": app_id,
            "name": data.get("name") or search_data.get("name") or game_title,
            "steam_url": f"https://store.steampowered.com/app/{app_id}",
            "price": price,
            "review_count": review_count,
            "review_percent": None,  # Not reliably available in appdetails payload.
            "release_date": data.get("release_date", {}).get("date"),
        }

    async def _search(self, game_title: str) -> dict[str, Any] | None:
        params = {"term": game_title, "l": "en", "cc": "US"}
        async with aiohttp.ClientSession() as session:
            async with session.get(SEARCH_URL, params=params, timeout=20) as response:
                if response.status != 200:
                    return None
                payload = await response.json()

        items = payload.get("items") or []
        return items[0] if items else None

    async def _app_details(self, app_id: str) -> dict[str, Any] | None:
        params = {"appids": app_id}
        async with aiohttp.ClientSession() as session:
            async with session.get(APP_DETAILS_URL, params=params, timeout=20) as response:
                if response.status != 200:
                    return None
                payload = await response.json()

        app_payload = payload.get(app_id)
        if not app_payload or not app_payload.get("success"):
            return None
        return app_payload


def _extract_price(app_data: dict[str, Any]) -> str:
    price_overview = app_data.get("price_overview")
    if not price_overview:
        return "Free / N/A"

    final_formatted = price_overview.get("final_formatted")
    if final_formatted:
        return final_formatted

    final_cents = price_overview.get("final")
    currency = price_overview.get("currency", "USD")
    if isinstance(final_cents, int):
        return f"{currency} {final_cents / 100:.2f}"

    return "N/A"
