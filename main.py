import os
import logging
import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_API")

logging.basicConfig(
    format="%(asctime)s - %(name)s %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot_log.txt"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
stats = {"scams": 0, "nsfw": 0, "start_time": datetime.datetime.now()}

BANNED_WORDS = [
    "crypto",
    "hentai",
    "airdrop",
    "porn",
    "sexfree money",
]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.username} triggered /hello")
    uptime = datetime.datetime.now() - stats["start_time"]
    await update.message.reply_text(
        f"✅ **Bot is Online!**\n"
        f"⏱ Uptime: {str(uptime).split('.')[0]}\n"
        f"🛡 Scams blocked: {stats['scams']}\n"
        f"🔞 NSFW blocked: {stats['nsfw']}"
    )


async def moderator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower() if update.message.text else ""

    if any(word in text for word in BANNED_WORDS):
        try:
            await update.message.delete()
            await update.message.reply_text(
                f"Deleted message {update.message} from {
                    update.message.from_user.username
                }"
            )
        except Exception as e:
            await update.message.reply_text(f"Failed to delete: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), moderator))
    app.add_handler(CommandHandler("hello", start_command))
    logger.info("Shams started. Listening for messages")
    app.run_polling()


if __name__ == "__main__":
    main()
