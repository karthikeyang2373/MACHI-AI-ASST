import pyautogui
from typing import Tuple
from utils.logger import logger

pyautogui.FAILSAFE = False


class MouseController:
    """Controls mouse: click, right-click, double-click."""

    def click(self) -> Tuple[bool, str]:
        try:
            pyautogui.click()
            return True, "Clicked."
        except Exception as e:
            logger.error(f"Click error: {e}")
            return False, "Could not click."

    def right_click(self) -> Tuple[bool, str]:
        try:
            pyautogui.rightClick()
            return True, "Right-clicked."
        except Exception as e:
            logger.error(f"Right click error: {e}")
            return False, "Could not right-click."

    def double_click(self) -> Tuple[bool, str]:
        try:
            pyautogui.doubleClick()
            return True, "Double-clicked."
        except Exception as e:
            logger.error(f"Double click error: {e}")
            return False, "Could not double-click."

    def execute_action(self, action: str) -> Tuple[bool, str]:
        if action == "click":
            return self.click()
        elif action == "right_click":
            return self.right_click()
        elif action == "double_click":
            return self.double_click()
        return False, "Unknown mouse action."


mouse_controller = MouseController()
