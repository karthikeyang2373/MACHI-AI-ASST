import pyautogui
import pygetwindow as gw
from typing import Tuple
from utils.logger import logger

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1


class WindowController:
    """Controls Windows application windows: minimize, maximize, restore, close, switch."""

    def minimize_window(self) -> Tuple[bool, str]:
        try:
            win = gw.getActiveWindow()
            if win:
                win.minimize()
                logger.info(f"Minimized window: {win.title}")
                return True, "Window minimized."
        except Exception as e:
            logger.error(f"Minimize error: {e}")
        # Fallback shortcut
        try:
            pyautogui.hotkey("win", "down")
            return True, "Window minimized."
        except Exception:
            return False, "Could not minimize window."

    def maximize_window(self) -> Tuple[bool, str]:
        try:
            win = gw.getActiveWindow()
            if win:
                win.maximize()
                logger.info(f"Maximized window: {win.title}")
                return True, "Window maximized."
        except Exception as e:
            logger.error(f"Maximize error: {e}")
        # Fallback shortcut
        try:
            pyautogui.hotkey("win", "up")
            return True, "Window maximized."
        except Exception:
            return False, "Could not maximize window."

    def restore_window(self) -> Tuple[bool, str]:
        try:
            win = gw.getActiveWindow()
            if win:
                win.restore()
                logger.info(f"Restored window: {win.title}")
                return True, "Window restored."
        except Exception as e:
            logger.error(f"Restore error: {e}")
        return False, "Could not restore window."

    def close_window(self) -> Tuple[bool, str]:
        try:
            win = gw.getActiveWindow()
            if win:
                win.close()
                logger.info(f"Closed window: {win.title}")
                return True, "Window closed."
        except Exception as e:
            logger.error(f"Close window error: {e}")
        # Fallback shortcut
        try:
            pyautogui.hotkey("alt", "f4")
            return True, "Window closed."
        except Exception:
            return False, "Could not close window."

    def switch_to_window(self, app_name: str) -> Tuple[bool, str]:
        try:
            windows = gw.getAllWindows()
            app_lower = app_name.lower().strip()
            for w in windows:
                if w.title and app_lower in w.title.lower():
                    if w.isMinimized:
                        w.restore()
                    w.activate()
                    logger.info(f"Switched to window: {w.title}")
                    return True, f"Switched to {app_name}."
            return False, f"No window found matching '{app_name}'."
        except Exception as e:
            logger.error(f"Switch window error: {e}")
            return False, f"Could not switch to {app_name}."

    def control_window(self, action: str, app_name: str = None) -> Tuple[bool, str]:
        if action == "minimize":
            return self.minimize_window()
        elif action == "maximize":
            return self.maximize_window()
        elif action == "restore":
            return self.restore_window()
        elif action == "close":
            return self.close_window()
        elif action == "switch" and app_name:
            return self.switch_to_window(app_name)
        return False, "Unknown window action."


window_controller = WindowController()
