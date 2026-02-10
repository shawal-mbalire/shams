# Shams - Telegram Moderation Bot

A telegram bot at an attempt to block pornographic and crypto scam messages on telegrams.

## Features

- 🛡️ Automated scam detection and removal
- 🔞 NSFW content filtering
- 👤 User violation tracking with auto-ban
- 🔧 Dynamic word list management (admin commands)
- 📊 Statistics tracking
- 🐳 Docker support
- 🚀 CI/CD with GitHub Actions

## Setup

1. Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. Copy your bot token
3. Create `.env` file:
   ```bash
   TELEGRAM_BOT_API=your_bot_token_here
   ```
4. Add your Telegram user ID to `config.json` admin_users list

## Running

### Using uv (recommended)
```bash
just serve
```

### Using Docker
```bash
just docker-build
just docker-run
```

### Manual
```bash
uv pip install -r pyproject.toml
python main.py
```

## Commands

- `/start` or `/hello` - Bot status and statistics
- `/stats` - Detailed statistics (admin only)
- `/ban <word>` - Add word to ban list (admin only)
- `/unban <word>` - Remove word from ban list (admin only)

## Configuration

Edit `config.json` to customize:
- `banned_words` - List of scam-related keywords
- `nsfw_words` - List of NSFW keywords
- `admin_users` - List of admin Telegram user IDs
- `ban_threshold` - Number of violations before auto-ban
- `auto_ban` - Enable/disable automatic banning

## Security

⚠️ **Important**: Never commit your `.env` file or bot token to git!

## CI/CD

Pushes to `main` trigger:
- Linting checks (ruff, black)
- Docker image build and push to GitHub Container Registry (GHCR)

Pull the image:
```bash
docker pull ghcr.io/OWNER/shams:main
```
