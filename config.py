"""Configuration management for the bot."""
import json
from pathlib import Path
from typing import Dict, List, Set

config_path = Path(__file__).parent / "config.json"


def load_config() -> Dict:
    """Load configuration from config.json."""
    with open(config_path, "r") as f:
        return json.load(f)


def save_config(config: Dict) -> None:
    """Save configuration to config.json."""
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_banned_words() -> List[str]:
    """Get list of banned words."""
    config = load_config()
    return config.get("banned_words", [])


def get_nsfw_words() -> List[str]:
    """Get list of NSFW words."""
    config = load_config()
    return config.get("nsfw_words", [])


def get_admin_users() -> Set[int]:
    """Get set of admin user IDs."""
    config = load_config()
    return set(config.get("admin_users", []))


def get_ban_threshold() -> int:
    """Get ban threshold."""
    config = load_config()
    return config.get("ban_threshold", 3)


def get_auto_ban() -> bool:
    """Get auto-ban setting."""
    config = load_config()
    return config.get("auto_ban", True)
