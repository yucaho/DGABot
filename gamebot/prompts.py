"""Prompt templates used by GameBot."""

ANALYZE_MESSAGES_PROMPT = """
You are analyzing a Discord conversation about video games.

Return STRICT JSON only.
Do not include markdown, code fences, or extra text.

Output format:
[
  {
    "game": "Game Title",
    "summary": "Short direct summary.",
    "sentiment": "Buy"
  }
]

Rules:
- Extract only actual game titles discussed by users.
- Summaries should be concise and neutral in tone.
- sentiment must be exactly one of: "Buy", "Buy on Sale", "Don't Buy".
- If no games are discussed, return []

Discord messages:
{messages}
""".strip()
