import pyautogui
import time
from typing import Tuple
from utils.logger import logger

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


class KeyboardController:
    """Controls keyboard input: typing, hotkeys, scroll, clipboard, and media playback."""

    def type_text(self, text: str) -> Tuple[bool, str]:
        try:
            time.sleep(0.2)
            pyautogui.typewrite(text, interval=0.03)
            logger.info(f"Typed text: '{text}'")
            return True, f"Typed: {text}"
        except Exception as e:
            logger.error(f"Type text error: {e}")
            return False, f"Could not type text: {e}"

    def press_key(self, key: str) -> Tuple[bool, str]:
        try:
            pyautogui.press(key.lower())
            logger.info(f"Pressed key: {key}")
            return True, f"Pressed {key}."
        except Exception as e:
            logger.error(f"Press key error: {e}")
            return False, f"Could not press {key}."

    def copy(self) -> Tuple[bool, str]:
        try:
            pyautogui.hotkey("ctrl", "c")
            return True, "Copied to clipboard."
        except Exception:
            return False, "Could not copy."

    def paste(self) -> Tuple[bool, str]:
        try:
            pyautogui.hotkey("ctrl", "v")
            return True, "Pasted from clipboard."
        except Exception:
            return False, "Could not paste."

    def select_all(self) -> Tuple[bool, str]:
        try:
            pyautogui.hotkey("ctrl", "a")
            return True, "Selected all."
        except Exception:
            return False, "Could not select all."

    def scroll_down(self, clicks: int = 5) -> Tuple[bool, str]:
        try:
            pyautogui.scroll(-clicks * 100)
            return True, "Scrolled down."
        except Exception:
            return False, "Could not scroll down."

    def scroll_up(self, clicks: int = 5) -> Tuple[bool, str]:
        try:
            pyautogui.scroll(clicks * 100)
            return True, "Scrolled up."
        except Exception:
            return False, "Could not scroll up."

    def media_control(self, action: str) -> Tuple[bool, str]:
        """Controls media playback: playpause, nexttrack, prevtrack."""
        try:
            if action in ["playpause", "play", "pause"]:
                pyautogui.press("playpause")
                return True, "Toggled media playback."
            elif action in ["nexttrack", "next"]:
                pyautogui.press("nexttrack")
                return True, "Skipped to next track."
            elif action in ["prevtrack", "prev", "previous"]:
                pyautogui.press("prevtrack")
                return True, "Went to previous track."
            return False, f"Unknown media action: {action}"
        except Exception as e:
            logger.error(f"Media control error: {e}")
            return False, "Could not control media."

    def execute_action(self, action: str, text: str = None, key: str = None) -> Tuple[bool, str]:
        if action == "type" and text:
            return self.type_text(text)
        elif action == "press" and key:
            return self.press_key(key)
        elif action == "copy":
            return self.copy()
        elif action == "paste":
            return self.paste()
        elif action == "select_all":
            return self.select_all()
        elif action == "scroll_down":
            return self.scroll_down()
        elif action == "scroll_up":
            return self.scroll_up()
        elif action in ["playpause", "nexttrack", "prevtrack"]:
            return self.media_control(action)
        return False, "Unknown keyboard action."


keyboard_controller = KeyboardController()
