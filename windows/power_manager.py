import os
import subprocess
import datetime
from typing import Tuple
from utils.logger import logger


class PowerManager:
    """Manages Windows power commands: shutdown, restart, sleep, lock."""

    def shutdown(self, delay_seconds: int = 10) -> Tuple[bool, str]:
        try:
            subprocess.Popen(["shutdown", "/s", "/t", str(delay_seconds)])
            logger.warning(f"Shutdown scheduled in {delay_seconds}s.")
            return True, f"PC will shut down in {delay_seconds} seconds."
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            return False, "Could not initiate shutdown."

    def restart(self, delay_seconds: int = 10) -> Tuple[bool, str]:
        try:
            subprocess.Popen(["shutdown", "/r", "/t", str(delay_seconds)])
            logger.warning(f"Restart scheduled in {delay_seconds}s.")
            return True, f"PC will restart in {delay_seconds} seconds."
        except Exception as e:
            logger.error(f"Restart error: {e}")
            return False, "Could not initiate restart."

    def sleep(self) -> Tuple[bool, str]:
        try:
            subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            logger.info("Sleep command issued.")
            return True, "Putting the PC to sleep."
        except Exception as e:
            logger.error(f"Sleep error: {e}")
            return False, "Could not put PC to sleep."

    def lock(self) -> Tuple[bool, str]:
        try:
            subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
            logger.info("Lock command issued.")
            return True, "Locking the PC."
        except Exception as e:
            logger.error(f"Lock error: {e}")
            return False, "Could not lock the PC."

    def cancel_shutdown(self) -> Tuple[bool, str]:
        try:
            subprocess.Popen(["shutdown", "/a"])
            logger.info("Shutdown/restart cancelled.")
            return True, "Shutdown cancelled."
        except Exception as e:
            return False, "Could not cancel shutdown."


power_manager = PowerManager()
