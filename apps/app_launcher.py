import os
import shutil
import subprocess
import psutil
from pathlib import Path
from typing import Tuple, List, Optional
from config import KNOWN_APPS
from memory.conversation_manager import conversation_manager
from utils.logger import logger


class AppLauncher:
    """Launches and manages Windows applications by name or system URI."""

    def open_app(self, app_name: str) -> Tuple[bool, str]:
        """Opens an application by its friendly name."""
        app_name_lower = app_name.strip().lower()

        # 1. Check known apps registry
        for key, executables in KNOWN_APPS.items():
            if app_name_lower == key or app_name_lower in key or key in app_name_lower:
                for exe in executables:
                    success, msg = self._launch(exe, app_name)
                    if success:
                        return True, msg

        # 2. Try URI schemes
        if "setting" in app_name_lower:
            return self._launch_uri("ms-settings:", "Settings")
        if "store" in app_name_lower:
            return self._launch_uri("ms-windows-store:", "Microsoft Store")
        if "camera" in app_name_lower:
            return self._launch_uri("microsoft.windows.camera:", "Camera")

        # 3. Check if executable exists in system PATH
        exe_clean = app_name_lower.replace(" ", "")
        if shutil.which(exe_clean):
            return self._launch(exe_clean, app_name)
        if shutil.which(exe_clean + ".exe"):
            return self._launch(exe_clean + ".exe", app_name)

        # 4. Search in Start Menu Shortcuts
        shortcut_match = self._find_start_menu_shortcut(app_name_lower)
        if shortcut_match:
            try:
                os.startfile(shortcut_match)
                conversation_manager.update_context("last_app", app_name)
                return True, f"Opening {app_name}."
            except Exception as e:
                logger.error(f"Shortcut launch error: {e}")

        # 5. Try launching with Windows `start` command
        try:
            subprocess.Popen(f"start {exe_clean}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            conversation_manager.update_context("last_app", app_name)
            return True, f"Attempting to launch {app_name}."
        except Exception:
            pass

        return False, f"I couldn't find an app called '{app_name}'. Make sure it is installed."

    def _find_start_menu_shortcut(self, query: str) -> Optional[str]:
        """Searches Windows Start Menu shortcut directories for matching .lnk files."""
        search_paths = [
            Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs",
            Path(os.environ.get("PROGRAMDATA", "")) / r"Microsoft\Windows\Start Menu\Programs"
        ]
        for base in search_paths:
            if not base.exists():
                continue
            for root, _, files in os.walk(base):
                for f in files:
                    if f.lower().endswith(".lnk") and query in f.lower():
                        return str(Path(root) / f)
        return None

    def _launch(self, target: str, display_name: str) -> Tuple[bool, str]:
        """Executes a target application or URI."""
        if target.endswith(":"):
            return self._launch_uri(target, display_name)
        try:
            subprocess.Popen(target, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            conversation_manager.update_context("last_app", display_name)
            logger.info(f"Launched application: {target}")
            return True, f"Opening {display_name}."
        except Exception as e:
            logger.error(f"Failed to launch '{target}': {e}")
            return False, f"Could not open {display_name}."

    def _launch_uri(self, uri: str, display_name: str) -> Tuple[bool, str]:
        """Launches a Windows URI scheme."""
        try:
            os.startfile(uri)
            conversation_manager.update_context("last_app", display_name)
            logger.info(f"Launched URI: {uri}")
            return True, f"Opening {display_name}."
        except Exception as e:
            logger.error(f"Failed to launch URI '{uri}': {e}")
            return False, f"Could not open {display_name}."

    def close_app(self, app_name: str) -> Tuple[bool, str]:
        """Closes a running application by matching process or window name."""
        app_name_lower = app_name.strip().lower()
        killed = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                proc_name = proc.info["name"].lower()
                clean_target = app_name_lower.replace(" ", "")
                if clean_target in proc_name or proc_name.startswith(clean_target):
                    proc.terminate()
                    killed.append(proc.info["name"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if killed:
            logger.info(f"Closed processes: {killed}")
            return True, f"Closed {app_name}."
        return False, f"I couldn't find '{app_name}' running."


app_launcher = AppLauncher()
