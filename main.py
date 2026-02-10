"""Telegram bot entry point."""
import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, filters, CommandHandler

from handlers import start_command, stats_command, ban_word_command, unban_word_command
from moderator import moderator

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_API")

logging.basicConfig(
    format="%(asctime)s - %(name)s %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot_log.txt"), logging.StreamHandler()],
)

# Prevent httpx from logging URLs containing bot token
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main():
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_API not set in environment")
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Message handlers (text + captions)
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.CAPTION) & (~filters.COMMAND),
        moderator
    ))
    
    # Command handlers
    app.add_handler(CommandHandler("hello", start_command))
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("ban", ban_word_command))
    app.add_handler(CommandHandler("unban", unban_word_command))
    
    logger.info("Shams started. Listening for messages")
    app.run_polling()


if __name__ == "__main__":
    main()
