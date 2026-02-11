"""Utility functions for text processing."""
import re
from typing import List, Tuple


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
    """Normalize text by removing special chars, extra spaces, and obfuscation."""
    # Remove emojis and special unicode
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove repeated characters (e.g., "cooool" -> "col")
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://[^\s]+|www\.[^\s]+|t\.me/[^\s]+'
    return re.findall(url_pattern, text, re.IGNORECASE)


def check_suspicious_patterns(text: str) -> List[Tuple[str, str]]:
    """Check for suspicious patterns in text. Returns list of (category, matched_text)."""
    patterns = [
        # Common crypto scam patterns
        (r'\b(?:airdrop|presale|claim|token)\s+(?:now|free|link)\b', 'crypto_scam'),
        (r'\b(?:double|triple)\s+(?:your|btc|eth|usdt)\b', 'crypto_scam'),
        (r'\b(?:earn|make|win)\s+\$?\d+', 'money_scam'),
        (r'\b\d+\s*(?:btc|eth|usdt|bitcoin|ethereum)', 'crypto_mention'),
        (r'\binvest\s+(?:with|now|today)', 'investment_scam'),
        (r'\bcontact\s+(?:me|us|admin)\s+(?:for|to)', 'contact_scam'),
        (r'\bclick\s+(?:here|link|below)', 'phishing'),
        (r'\bguaranteed\s+(?:profit|return|income)', 'scam'),
        (r'\b(?:dm|pm)\s+(?:me|for)', 'dm_scam'),
        
        # NSFW patterns
        (r'\b(?:18|21)\+\s*(?:only|content)\b', 'nsfw'),
        (r'\b(?:nude|naked|sex)\s+(?:pics?|photos?|videos?)\b', 'nsfw'),
        (r'\bonlyfans|fansly|patreon\s+(?:link|free)', 'nsfw_promo'),
        (r'\b(?:hot|sexy)\s+(?:girls?|boys?|pics?)', 'nsfw'),
    ]
    
    matches = []
    for pattern, category in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            match = re.search(pattern, text, re.IGNORECASE)
            matches.append((category, match.group()))
    
    return matches


def check_spam_indicators(text: str) -> int:
    """Check for spam indicators. Returns spam score (0-10)."""
    score = 0
    
    # Excessive emojis
    emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', text))
    if emoji_count > 5:
        score += min(emoji_count // 2, 3)
    
    # ALL CAPS
    if len(text) > 20 and text.isupper():
        score += 2
    
    # Excessive exclamation/question marks
    if text.count('!') > 3 or text.count('?') > 3:
        score += 1
    
    # Repeated words
    words = text.split()
    if len(words) > 5 and len(words) != len(set(words)):
        score += 2
    
    # URLs present
    if extract_urls(text):
        score += 2
    
    return min(score, 10)
