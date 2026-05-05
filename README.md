# GameBot

A portfolio-ready Python Discord bot that reads game discussion in a Discord channel, uses OpenAI to summarize sentiment by game title, enriches each game with Steam metadata, and stores channel-specific results for quick lookup.

## Screenshots

> Add screenshots here after deployment.

- `docs/images/analyze-output.png`
- `docs/images/summary-output.png`

## Features

- Discord bot built with `discord.py`
- `!analyze` command for recent channel discussion analysis
- OpenAI-powered game extraction + sentiment summaries
- Steam enrichment via async `aiohttp` (search + app details)
- Channel-scoped storage in `data/sentiments_<channel_id>.json`
- Sentiment grouping:
  - **Certified Banger** 🍆💦
  - **Wait for a Sale** 😬
  - **Hard Pass** ❌🗑️
- `!summary <game>` includes a clean Steam hyperlink with suppressed embeds

## Commands

- `!analyze`
- `!list`
- `!summary <game>`
- `!help` / `!gamebot`

## Setup

### 1) Clone

```powershell
git clone https://github.com/your-username/gamebot.git
cd gamebot
```

### 2) Create and activate virtual environment (PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```powershell
pip install -r requirements.txt
```

### 4) Create environment file

```powershell
copy .env.example .env
```

### 5) Update `.env`

```dotenv
DISCORD_TOKEN=your_discord_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
MESSAGE_FETCH_LIMIT=200
```

### 6) Discord bot configuration

- In the Discord Developer Portal, enable **Message Content Intent**.
- Invite the bot to your server with proper permissions (read/send messages).

### 7) Run

```powershell
python gamebot/bot.py
```

## Usage examples

```text
!analyze
!list
!summary Elden Ring
```

## Troubleshooting

- **ModuleNotFoundError**
  - Make sure your virtual environment is activated and `pip install -r requirements.txt` completed.
- **Message Content Intent missing**
  - Re-check the bot settings in Discord Developer Portal.
- **Discord 2000 character limit**
  - Reduce `MESSAGE_FETCH_LIMIT` in `.env` or split outputs.
- **Steam data unavailable**
  - Steam endpoint may not return app data for every search term. Try a more exact game title.

## Future roadmap

- Steam upcoming releases
- Price alerts
- User voting and consensus scores
- Sentiment history tracking
- Web dashboard
