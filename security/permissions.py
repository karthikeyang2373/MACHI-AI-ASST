from typing import Dict
from config import DEFAULT_PERMISSIONS
from utils.logger import logger

class PermissionManager:
    """Manages and enforces security permissions for MACHI features."""

    def __init__(self):
        self._permissions: Dict[str, str] = DEFAULT_PERMISSIONS.copy()

    def get_permission(self, key: str) -> str:
        """Returns permission status for key ('ENABLED', 'CONFIRM', or 'DISABLED')."""
        return self._permissions.get(key, "CONFIRM")

    def set_permission(self, key: str, status: str) -> bool:
        """Sets permission status for a given key."""
        if status.upper() in ["ENABLED", "CONFIRM", "DISABLED"]:
            self._permissions[key] = status.upper()
            logger.info(f"Permission '{key}' updated to '{status.upper()}'.")
            return True
        return False

    def is_allowed(self, category: str) -> bool:
        """Checks if a category is allowed (either ENABLED or CONFIRM)."""
        status = self.get_permission(category)
        return status != "DISABLED"

    def requires_confirmation(self, category: str) -> bool:
        """Checks if a category explicitly requires user confirmation."""
        status = self.get_permission(category)
        return status == "CONFIRM"

    def get_all_permissions(self) -> Dict[str, str]:
        """Returns all permission settings."""
        return self._permissions.copy()

permission_manager = PermissionManager()