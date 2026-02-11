"""Utility functions for text processing."""
import re


def extract_text(message) -> str:
    """Extract all text from message including captions and forwarded content."""
    text_parts = []
    
    if message.text:
        text_parts.append(message.text)
    
    if message.caption:
        text_parts.append(message.caption)
    
    # Check for forwarded messages (newer API uses forward_origin)
    if hasattr(message, 'forward_origin') and message.forward_origin:
        if hasattr(message.forward_origin, 'sender_user') and message.forward_origin.sender_user:
            user = message.forward_origin.sender_user
            if user.first_name:
                text_parts.append(user.first_name)
            if user.username:
                text_parts.append(user.username)
    
    return " ".join(text_parts).lower()


def normalize_text(text: str) -> str:
    """Normalize text by removing special chars and extra spaces."""
    # Remove special characters
    normalized = re.sub(r"[^a-z0-9\s]", " ", text)
    # Remove extra spaces
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()
