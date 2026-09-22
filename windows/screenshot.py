import pyautogui
import datetime
from typing import Tuple
from config import SCREENSHOTS_DIR
from utils.helpers import get_timestamp_str
from utils.logger import logger


class ScreenshotManager:
    """Captures and saves screenshots."""

    def take_screenshot(self) -> Tuple[bool, str]:
        try:
            timestamp = get_timestamp_str()
            filename = f"screenshot_{timestamp}.png"
            filepath = SCREENSHOTS_DIR / filename
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            return True, f"Screenshot saved to Pictures folder as {filename}."
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return False, "Could not take screenshot."


screenshot_manager = ScreenshotManager()
