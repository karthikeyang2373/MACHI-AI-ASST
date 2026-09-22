from typing import Tuple
from utils.logger import logger

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    import comtypes
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    logger.warning("pycaw not available. Volume control will be limited.")

import pyautogui


class VolumeController:
    """Controls Windows system volume using pycaw or pyautogui fallback."""

    def _get_volume_interface(self):
        if not PYCAW_AVAILABLE:
            return None
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            logger.error(f"Volume interface error: {e}")
            return None

    def increase_volume(self, step: float = 0.1) -> Tuple[bool, str]:
        volume = self._get_volume_interface()
        if volume:
            try:
                current = volume.GetMasterVolumeLevelScalar()
                new_vol = min(1.0, current + step)
                volume.SetMasterVolumeLevelScalar(new_vol, None)
                return True, f"Volume increased to {int(new_vol * 100)} percent."
            except Exception as e:
                logger.error(f"Increase volume error: {e}")
        # Fallback
        pyautogui.press("volumeup")
        return True, "Volume increased."

    def decrease_volume(self, step: float = 0.1) -> Tuple[bool, str]:
        volume = self._get_volume_interface()
        if volume:
            try:
                current = volume.GetMasterVolumeLevelScalar()
                new_vol = max(0.0, current - step)
                volume.SetMasterVolumeLevelScalar(new_vol, None)
                return True, f"Volume decreased to {int(new_vol * 100)} percent."
            except Exception as e:
                logger.error(f"Decrease volume error: {e}")
        pyautogui.press("volumedown")
        return True, "Volume decreased."

    def mute(self) -> Tuple[bool, str]:
        volume = self._get_volume_interface()
        if volume:
            try:
                volume.SetMute(1, None)
                return True, "Volume muted."
            except Exception as e:
                logger.error(f"Mute error: {e}")
        pyautogui.press("volumemute")
        return True, "Volume muted."

    def unmute(self) -> Tuple[bool, str]:
        volume = self._get_volume_interface()
        if volume:
            try:
                volume.SetMute(0, None)
                return True, "Volume unmuted."
            except Exception as e:
                logger.error(f"Unmute error: {e}")
        pyautogui.press("volumemute")
        return True, "Volume unmuted."

    def set_volume(self, level: int) -> Tuple[bool, str]:
        """Sets volume to a specific level (0-100)."""
        level = max(0, min(100, int(level)))
        volume = self._get_volume_interface()
        if volume:
            try:
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                return True, f"Volume set to {level} percent."
            except Exception as e:
                logger.error(f"Set volume error: {e}")
        return False, "Could not set volume level."

    def execute_action(self, action: str, level: int = None) -> Tuple[bool, str]:
        if action == "increase":
            return self.increase_volume()
        elif action == "decrease":
            return self.decrease_volume()
        elif action == "mute":
            return self.mute()
        elif action == "unmute":
            return self.unmute()
        elif action == "set" and level is not None:
            return self.set_volume(level)
        return False, "Unknown volume action."


volume_controller = VolumeController()
