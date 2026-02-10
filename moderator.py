"""Message moderation logic."""
import logging
import datetime
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes

from config import get_banned_words, get_nsfw_words, get_ban_threshold, get_auto_ban
from utils import extract_text, normalize_text

logger = logging.getLogger(__name__)

# Global state
stats = {"scams": 0, "nsfw": 0, "start_time": datetime.datetime.now()}
user_violations = defaultdict(int)


async def moderator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check messages for banned content and moderate."""
    # Extract all text from message
    text = extract_text(update.message)
    if not text:
        return
    
    # Normalize text (remove extra spaces, special chars)
    normalized_text = normalize_text(text)
    
    user_id = update.effective_user.id
    username = update.effective_user.username or f"user_{user_id}"
    
    # Check for banned words (scams)
    matched_banned = [word for word in get_banned_words() if word in normalized_text]
    # Check for NSFW
    matched_nsfw = [word for word in get_nsfw_words() if word in normalized_text]
    
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
            if get_auto_ban() and user_violations[user_id] >= get_ban_threshold():
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
