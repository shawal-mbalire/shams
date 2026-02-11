"""Command handlers for the bot."""
import datetime
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    get_admin_users,
    load_config,
    save_config,
)
from moderator import stats, user_violations


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start and /hello commands."""
    await update.message.reply_text(
        "🤖 **Shams Moderation Bot**\n\n"
        "I automatically detect and remove:\n"
        "• Scam messages (crypto, airdrops, fake investments)\n"
        "• NSFW content\n\n"
        "Commands:\n"
        "/start - This message\n"
        "/whoami - Get your user ID\n"
        "/stats - Statistics (admin only)\n"
        "/ban <word> - Ban a word (admin only)\n"
        "/unban <word> - Unban a word (admin only)"
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed statistics (admin only)."""
    user_id = update.effective_user.id
    if user_id not in get_admin_users():
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
        for uid, count in top_violators:
            msg += f"  • User {uid}: {count} violations\n"
    
    await update.message.reply_text(msg)


async def ban_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add word to ban list (admin only)."""
    user_id = update.effective_user.id
    if user_id not in get_admin_users():
        await update.message.reply_text("❌ Admin only command")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban <word>")
        return
    
    word = " ".join(context.args).lower()
    config = load_config()
    banned_words = config.get("banned_words", [])
    
    if word not in banned_words:
        banned_words.append(word)
        config["banned_words"] = banned_words
        save_config(config)
        await update.message.reply_text(f"✅ Banned word: {word}")
    else:
        await update.message.reply_text(f"⚠️ Word already banned: {word}")


async def unban_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove word from ban list (admin only)."""
    user_id = update.effective_user.id
    if user_id not in get_admin_users():
        await update.message.reply_text("❌ Admin only command")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban <word>")
        return
    
    word = " ".join(context.args).lower()
    config = load_config()
    banned_words = config.get("banned_words", [])
    
    if word in banned_words:
        banned_words.remove(word)
        config["banned_words"] = banned_words
        save_config(config)
        await update.message.reply_text(f"✅ Unbanned word: {word}")
    else:
        await update.message.reply_text(f"⚠️ Word not found: {word}")


async def whoami_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show your Telegram user ID."""
    user_id = update.effective_user.id if update.effective_user else 0
    username = update.effective_user.username if update.effective_user else "unknown"
    await update.message.reply_text(
        f"👤 Your Info:\n"
        f"ID: {user_id}\n"
        f"Username: @{username if username else 'none'}"
    )
