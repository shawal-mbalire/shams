import os
import logging
import datetime
import json
import re
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update, ChatMember
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

# Prevent httpx from logging URLs containing bot token
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
stats = {"scams": 0, "nsfw": 0, "start_time": datetime.datetime.now()}
user_violations = defaultdict(int)

# Load configuration
config_path = Path(__file__).parent / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)

BANNED_WORDS = config.get("banned_words", [])
NSFW_WORDS = config.get("nsfw_words", [])
ADMIN_USERS = set(config.get("admin_users", []))
BAN_THRESHOLD = config.get("ban_threshold", 3)
AUTO_BAN = config.get("auto_ban", True)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.username} triggered /hello")
    uptime = datetime.datetime.now() - stats["start_time"]
    await update.message.reply_text(
        f"✅ **Bot is Online!**\n"
        f"⏱ Uptime: {str(uptime).split('.')[0]}\n"
        f"🛡 Scams blocked: {stats['scams']}\n"
        f"🔞 NSFW blocked: {stats['nsfw']}\n"
        f"👥 Users warned: {len(user_violations)}"
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed statistics (admin only)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_USERS:
        await update.message.reply_text("❌ Admin only command")
        return
    
    uptime = datetime.datetime.now() - stats["start_time"]
    top_violators = sorted(user_violations.items(), key=lambda x: x[1], reverse=True)[:5]
    
    msg = (
        f"📊 **Bot Statistics**\n"
        f"⏱ Uptime: {str(uptime).split('.')[0]}\n"
        f"🛡 Scams blocked: {stats['scams']}\n"
        f"🔞 NSFW blocked: {stats['nsfw']}\n"
        f"👥 Users tracked: {len(user_violations)}\n\n"
    )
    
    if top_violators:
        msg += "Top violators:\n"
        for user_id, count in top_violators:
            msg += f"  • User {user_id}: {count} violations\n"
    
    await update.message.reply_text(msg)


async def ban_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add word to ban list (admin only)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_USERS:
        await update.message.reply_text("❌ Admin only command")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban <word>")
        return
    
    word = " ".join(context.args).lower()
    if word not in BANNED_WORDS:
        BANNED_WORDS.append(word)
        _save_config()
        await update.message.reply_text(f"✅ Banned word: {word}")
    else:
        await update.message.reply_text(f"⚠️ Word already banned: {word}")


async def unban_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove word from ban list (admin only)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_USERS:
        await update.message.reply_text("❌ Admin only command")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban <word>")
        return
    
    word = " ".join(context.args).lower()
    if word in BANNED_WORDS:
        BANNED_WORDS.remove(word)
        _save_config()
        await update.message.reply_text(f"✅ Unbanned word: {word}")
    else:
        await update.message.reply_text(f"⚠️ Word not found: {word}")


def _save_config():
    """Save current config to file"""
    config["banned_words"] = BANNED_WORDS
    config["nsfw_words"] = NSFW_WORDS
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def _extract_text(message) -> str:
    """Extract all text from message including captions and forwarded content"""
    text_parts = []
    
    if message.text:
        text_parts.append(message.text)
    
    if message.caption:
        text_parts.append(message.caption)
    
    if message.forward_from:
        if message.forward_from.first_name:
            text_parts.append(message.forward_from.first_name)
        if message.forward_from.username:
            text_parts.append(message.forward_from.username)
    
    return " ".join(text_parts).lower()


async def moderator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract all text from message
    text = _extract_text(update.message)
    if not text:
        return
    
    # Normalize text (remove extra spaces, special chars)
    normalized_text = re.sub(r"[^a-z0-9\s]", " ", text)
    normalized_text = re.sub(r"\s+", " ", normalized_text)
    
    user_id = update.effective_user.id
    username = update.effective_user.username or f"user_{user_id}"
    
    # Check for banned words (scams)
    matched_banned = [word for word in BANNED_WORDS if word in normalized_text]
    # Check for NSFW
    matched_nsfw = [word for word in NSFW_WORDS if word in normalized_text]
    
    if matched_banned or matched_nsfw:
        violation_type = "scam" if matched_banned else "nsfw"
        matched_words = matched_banned or matched_nsfw
        
        # Update stats
        if matched_banned:
            stats["scams"] += 1
        else:
            stats["nsfw"] += 1
        
        # Track user violations
        user_violations[user_id] += 1
        
        try:
            # Delete the offending message
            await update.message.delete()
            logger.warning(
                f"Deleted {violation_type} message from {username} (user_id={user_id}): "
                f"matched {matched_words[:3]}. Total violations: {user_violations[user_id]}"
            )
            
            # Ban user if threshold exceeded
            if AUTO_BAN and user_violations[user_id] >= BAN_THRESHOLD:
                try:
                    await context.bot.ban_chat_member(
                        chat_id=update.effective_chat.id,
                        user_id=user_id
                    )
                    logger.warning(f"Banned user {username} (user_id={user_id}) after {user_violations[user_id]} violations")
                except Exception as ban_error:
                    logger.error(f"Failed to ban user {user_id}: {ban_error}")
            
        except Exception as e:
            logger.error(f"Failed to delete message from {username}: {e}")


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
