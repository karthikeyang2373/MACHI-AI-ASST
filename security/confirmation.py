import threading
from typing import Callable, Optional
from utils.logger import logger

class ConfirmationManager:
    """Manages voice and GUI confirmation prompts for risky actions."""

    def __init__(self):
        self._pending_confirmation: Optional[dict] = None
        self._gui_callback: Optional[Callable] = None
        self._lock = threading.Lock()

    def register_gui_callback(self, callback: Callable):
        """Registers a GUI callback to trigger confirmation dialog modal."""
        self._gui_callback = callback

    def request_confirmation(self, action_description: str, on_confirm: Callable, on_cancel: Callable = None) -> dict:
        """
        Registers a pending confirmation request.
        """
        with self._lock:
            self._pending_confirmation = {
                "description": action_description,
                "on_confirm": on_confirm,
                "on_cancel": on_cancel
            }
            logger.info(f"Confirmation requested for: {action_description}")

        # Trigger GUI confirmation dialog if registered
        if self._gui_callback:
            try:
                self._gui_callback(action_description, self.confirm, self.cancel)
            except Exception as e:
                logger.error(f"Failed to show GUI confirmation modal: {e}")

        return self._pending_confirmation

    def has_pending(self) -> bool:
        """Returns True if there is an active confirmation waiting."""
        with self._lock:
            return self._pending_confirmation is not None

    def get_pending_description(self) -> str:
        """Returns description of pending confirmation."""
        with self._lock:
            if self._pending_confirmation:
                return self._pending_confirmation["description"]
            return ""

    def confirm(self) -> str:
        """User confirmed action."""
        with self._lock:
            if not self._pending_confirmation:
                return "No action pending confirmation."
            cb = self._pending_confirmation.get("on_confirm")
            desc = self._pending_confirmation.get("description", "Action")
            self._pending_confirmation = None

        if cb:
            try:
                cb()
                logger.info(f"Action confirmed and executed: {desc}")
                return f"Confirmed. Executing {desc}."
            except Exception as e:
                logger.error(f"Error executing confirmed action: {e}")
                return f"Error executing action: {e}"
        return "Action confirmed."

    def cancel(self) -> str:
        """User canceled action."""
        with self._lock:
            if not self._pending_confirmation:
                return "No action pending confirmation."
            cb = self._pending_confirmation.get("on_cancel")
            desc = self._pending_confirmation.get("description", "Action")
            self._pending_confirmation = None

        if cb:
            try:
                cb()
            except Exception as e:
                logger.error(f"Error during cancellation callback: {e}")
        logger.info(f"Action canceled by user: {desc}")
        return f"Canceled action: {desc}."

confirmation_manager = ConfirmationManager()