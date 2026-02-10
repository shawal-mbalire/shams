"""Utility functions for text processing."""
import re


def extract_text(message) -> str:
    """Extract all text from message including captions and forwarded content."""
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


def normalize_text(text: str) -> str:
    """Normalize text by removing special chars and extra spaces."""
    # Remove special characters
    normalized = re.sub(r"[^a-z0-9\s]", " ", text)
    # Remove extra spaces
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()
