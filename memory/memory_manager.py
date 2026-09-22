from typing import Optional, Dict
from memory.database import db_manager
from utils.logger import logger

class MemoryManager:
    """High-level persistent memory interface for user preferences and custom aliases."""

    def __init__(self):
        self.db = db_manager

    def set_user_preference(self, key: str, value: str):
        """Saves a user preference."""
        self.db.set_preference(key, value)
        logger.info(f"Memory saved preference: {key} = {value}")

    def get_user_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a user preference."""
        return self.db.get_preference(key, default)

    def set_app_alias(self, alias: str, target: str):
        """Saves a custom app/browser alias."""
        self.db.set_alias(alias, target)
        logger.info(f"Memory saved alias: {alias} -> {target}")

    def resolve_app_alias(self, alias: str) -> Optional[str]:
        """Resolves alias to target application or path."""
        return self.db.get_alias(alias)

    def get_default_browser(self) -> str:
        """Returns preferred browser name or fallback 'chrome'."""
        pref = self.get_user_preference("default_browser")
        return pref if pref else "chrome"

memory_manager = MemoryManager()
