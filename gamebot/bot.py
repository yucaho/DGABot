"""Discord GameBot entry point."""

from __future__ import annotations

import asyncio

import discord
from discord.ext import commands

from gamebot.config import MESSAGE_FETCH_LIMIT, validate_config
from gamebot.formatting import CATEGORIES, EMOJIS, group_by_sentiment, normalize_sentiment, render_game_line
from gamebot.openai_client import OpenAIAnalyzer
from gamebot.steam_client import SteamClient
from gamebot.storage import load_channel_sentiments, save_channel_sentiments

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
openai_analyzer = OpenAIAnalyzer()
steam_client = SteamClient()


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.command(name="analyze")
async def analyze(ctx: commands.Context) -> None:
    await ctx.send("Analyzing recent messages...")

    messages: list[str] = []
    async for message in ctx.channel.history(limit=MESSAGE_FETCH_LIMIT):
        if message.author.bot:
            continue
        content = message.content.strip()
        if content:
            messages.append(f"{message.author.display_name}: {content}")

    if not messages:
        await ctx.send("No recent user messages found in this channel.")
        return

    transcript = "\n".join(reversed(messages))

    try:
        analysis_rows = await asyncio.to_thread(openai_analyzer.analyze_messages, transcript)
    except Exception as exc:
        await ctx.send(f"OpenAI analysis failed: {exc}")
        return

    enriched_rows = []
    for row in analysis_rows:
        game = str(row.get("game", "")).strip()
        summary = str(row.get("summary", "")).strip() or "No summary available."
        raw_sentiment = str(row.get("sentiment", "Buy on Sale"))
        normalized = normalize_sentiment(raw_sentiment)

        if not game:
            continue

        steam_data = await steam_client.fetch_game(game)
        enriched_rows.append(
            {
                "game": game,
                "summary": summary,
                "sentiment": normalized,
                "steam_url": steam_data.get("steam_url") if steam_data else None,
                "price": steam_data.get("price", "N/A") if steam_data else "N/A",
                "review_count": steam_data.get("review_count") if steam_data else None,
                "review_percent": steam_data.get("review_percent") if steam_data else None,
                "app_id": steam_data.get("app_id") if steam_data else None,
                "release_date": steam_data.get("release_date") if steam_data else None,
                "name": steam_data.get("name") if steam_data else game,
            }
        )

    save_channel_sentiments(ctx.channel.id, enriched_rows)

    if not enriched_rows:
        await ctx.send("No games were confidently identified in recent messages.")
        return

    grouped = group_by_sentiment(enriched_rows)
    lines = ["## Game sentiment analysis"]
    for category in CATEGORIES:
        lines.append(f"\n**{category}** {EMOJIS[category]}")
        games = grouped.get(category, [])
        if not games:
            lines.append("- None")
            continue
        for item in games:
            lines.append(f"- {item['game']}")

    await ctx.send("\n".join(lines))


@bot.command(name="summary")
async def summary(ctx: commands.Context, *, game: str) -> None:
    rows = load_channel_sentiments(ctx.channel.id)
    match = next((r for r in rows if r.get("game", "").lower() == game.lower()), None)
    if not match:
        await ctx.send(f"No saved summary for '{game}' in this channel.")
        return

    await ctx.send(render_game_line(match), suppress_embeds=True)


@bot.command(name="list")
async def list_games(ctx: commands.Context) -> None:
    rows = load_channel_sentiments(ctx.channel.id)
    if not rows:
        await ctx.send("No saved sentiment data for this channel. Run !analyze first.")
        return

    grouped = group_by_sentiment(rows)
    lines = ["## Saved game sentiments"]
    for category in CATEGORIES:
        lines.append(f"\n**{category}** {EMOJIS[category]}")
        entries = grouped.get(category, [])
        if not entries:
            lines.append("- None")
            continue
        for item in entries:
            lines.append(f"- {item.get('game', 'Unknown Game')}")

    await ctx.send("\n".join(lines))


@bot.command(name="help")
@bot.command(name="gamebot")
async def help_command(ctx: commands.Context) -> None:
    message = """
**GameBot Commands**
- `!analyze` Analyze recent channel messages for game sentiment.
- `!list` Show saved game sentiment groups for this channel.
- `!summary <game>` Show detailed saved summary for a game.
- `!help` or `!gamebot` Show this message.

Setup:
1. Add DISCORD_TOKEN and OPENAI_API_KEY to `.env`.
2. Enable Message Content Intent in Discord Developer Portal.
3. Run with: `python gamebot/bot.py`
""".strip()
    await ctx.send(message)


if __name__ == "__main__":
    validate_config()
    bot.run(__import__("gamebot.config", fromlist=["DISCORD_TOKEN"]).DISCORD_TOKEN)
