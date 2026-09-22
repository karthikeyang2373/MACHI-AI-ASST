from enum import IntEnum
from typing import Dict, Any, Tuple
from utils.logger import logger
from security.permissions import permission_manager

class CommandLevel(IntEnum):
    SAFE = 1        # Execute immediately
    MODERATE = 2    # Require confirmation if set or user-sensitive
    HIGH_RISK = 3   # ALWAYS require explicit user confirmation

# Map intents to CommandLevel and required permission category
INTENT_SAFETY_MAP: Dict[str, Tuple[CommandLevel, str]] = {
    # Safe Level 1 Actions
    "OPEN_APP": (CommandLevel.SAFE, "application_access"),
    "OPEN_FOLDER": (CommandLevel.SAFE, "file_access"),
    "SEARCH_FILE": (CommandLevel.SAFE, "file_access"),
    "OPEN_FILE": (CommandLevel.SAFE, "file_access"),
    "SEARCH_WEB": (CommandLevel.SAFE, "browser_access"),
    "OPEN_WEBSITE": (CommandLevel.SAFE, "browser_access"),
    "SCREENSHOT": (CommandLevel.SAFE, "system_information"),
    "SYSTEM_INFO": (CommandLevel.SAFE, "system_information"),
    "VOLUME_CONTROL": (CommandLevel.SAFE, "system_information"),
    "WINDOW_CONTROL": (CommandLevel.SAFE, "system_information"),
    "AI_QUERY": (CommandLevel.SAFE, "browser_access"),

    # Moderate Level 2 Actions
    "CLOSE_APP": (CommandLevel.MODERATE, "application_access"),
    "CREATE_FILE": (CommandLevel.MODERATE, "file_access"),
    "CREATE_FOLDER": (CommandLevel.MODERATE, "file_access"),
    "COPY_FILE": (CommandLevel.MODERATE, "file_access"),
    "MOVE_FILE": (CommandLevel.MODERATE, "file_access"),
    "RENAME_FILE": (CommandLevel.MODERATE, "file_access"),
    "KEYBOARD_ACTION": (CommandLevel.MODERATE, "keyboard_control"),
    "MOUSE_ACTION": (CommandLevel.MODERATE, "mouse_control"),

    # High Risk Level 3 Actions
    "DELETE_FILE": (CommandLevel.HIGH_RISK, "file_deletion"),
    "DELETE_FOLDER": (CommandLevel.HIGH_RISK, "file_deletion"),
    "POWER_SHUTDOWN": (CommandLevel.HIGH_RISK, "power_commands"),
    "POWER_RESTART": (CommandLevel.HIGH_RISK, "power_commands"),
    "POWER_SLEEP": (CommandLevel.HIGH_RISK, "power_commands"),
    "POWER_LOCK": (CommandLevel.HIGH_RISK, "power_commands"),
    "SYSTEM_CHANGE": (CommandLevel.HIGH_RISK, "system_changes"),
}

class CommandSafetyEngine:
    """Evaluates and enforces security rules before intent execution."""

    @staticmethod
    def evaluate(intent: str, params: Dict[str, Any] = None) -> Tuple[bool, CommandLevel, str]:
        """
        Evaluates intent safety.
        Returns: (is_allowed, command_level, message)
        """
        if intent not in INTENT_SAFETY_MAP:
            # Default unknown intents to Moderate safety check
            return True, CommandLevel.MODERATE, "Unknown intent requires evaluation."

        level, permission_cat = INTENT_SAFETY_MAP[intent]

        # Check if feature category is disabled by user permissions
        if not permission_manager.is_allowed(permission_cat):
            msg = f"Feature category '{permission_cat}' is disabled in MACHI security settings."
            logger.warning(msg)
            return False, level, msg

        # Check if permission manager forces confirmation for category
        if permission_manager.requires_confirmation(permission_cat):
            level = max(level, CommandLevel.MODERATE)

        return True, level, "Command allowed."

    @staticmethod
    def is_shell_command_safe(cmd_str: str) -> bool:
        """
        Guards against arbitrary voice shell execution.
        Prevents dangerous shell injections and raw os.system calls.
        """
        forbidden_keywords = [
            "rm -rf", "del /f /s /q", "format", "diskpart",
            "net user", "reg delete", "powershell -enc", "vssadmin"
        ]
        cmd_lower = cmd_str.lower()
        for kw in forbidden_keywords:
            if kw in cmd_lower:
                logger.critical(f"Forbidden command keyword detected: '{kw}'")
                return False
        return True

safety_engine = CommandSafetyEngine()