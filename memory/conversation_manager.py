from typing import Optional, Dict, Any, List
from memory.database import db_manager
from utils.logger import logger

class ConversationManager:
    """Manages short-term conversation context for multi-step & follow-up commands."""

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.db = db_manager
        self._context: Dict[str, Any] = {
            "last_folder": None,
            "last_file": None,
            "last_app": None,
            "last_search_query": None,
            "last_intent": None
        }

    def update_context(self, key: str, value: Any):
        """Updates a context parameter."""
        self._context[key] = value
        logger.debug(f"Context updated: {key} = {value}")

    def get_context(self, key: str, default: Any = None) -> Any:
        """Retrieves a context parameter."""
        return self._context.get(key, default)

    def log_user_message(self, text: str, intent: Optional[str] = None):
        """Logs user message to conversation history."""
        self.db.log_chat(sender="User", message=text, intent=intent)
        if intent:
            self._context["last_intent"] = intent

    def log_assistant_message(self, text: str):
        """Logs MACHI assistant message to conversation history."""
        self.db.log_chat(sender="MACHI", message=text)

    def get_recent_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves recent conversation messages."""
        return self.db.get_chat_history(limit=limit)

conversation_manager = ConversationManager()
