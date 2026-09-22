"""
MACHI Core Command Dispatcher
Routes detected intents to the correct handler modules.
"""
import os
from pathlib import Path
from typing import Tuple, Dict, Any, Callable, Optional
from utils.logger import logger
from ai.gemini import gemini_client
from memory.conversation_manager import conversation_manager
from memory.database import db_manager
from security.command_safety import safety_engine, CommandLevel
from security.confirmation import confirmation_manager


def _get_handlers():
    from apps.app_launcher import app_launcher
    from browser.web_handler import web_handler
    from files.folder_manager import folder_manager
    from files.file_search import file_search_engine
    from windows.system_info import system_monitor
    from windows.power_manager import power_manager
    from windows.window_controller import window_controller
    from windows.keyboard_controller import keyboard_controller
    from windows.mouse_controller import mouse_controller
    from windows.screenshot import screenshot_manager
    from windows.volume_controller import volume_controller
    return {
        "app_launcher": app_launcher,
        "web_handler": web_handler,
        "folder_manager": folder_manager,
        "file_search_engine": file_search_engine,
        "system_monitor": system_monitor,
        "power_manager": power_manager,
        "window_controller": window_controller,
        "keyboard_controller": keyboard_controller,
        "mouse_controller": mouse_controller,
        "screenshot_manager": screenshot_manager,
        "volume_controller": volume_controller,
    }


class CommandDispatcher:
    """Routes voice command intents to the appropriate action handlers."""

    def __init__(self):
        self._handlers = None
        self._on_confirmation_needed: Optional[Callable] = None
        self._on_response: Optional[Callable] = None

    def _h(self):
        if self._handlers is None:
            self._handlers = _get_handlers()
        return self._handlers

    def set_callbacks(self, on_response: Callable = None, on_confirmation_needed: Callable = None):
        """Set callbacks for response and confirmation dialog."""
        self._on_response = on_response
        self._on_confirmation_needed = on_confirmation_needed

    def dispatch(self, raw_input: str, intent: str, params: Dict[str, Any]) -> str:
        """
        Main dispatcher. Routes intent to the correct handler.
        Returns response string.
        """
        # Safety evaluation
        is_allowed, level, safety_msg = safety_engine.evaluate(intent, params)

        if not is_allowed:
            db_manager.log_command(raw_input, intent, "BLOCKED", safety_msg)
            return safety_msg

        # Handle high-risk commands with confirmation
        if level == CommandLevel.HIGH_RISK:
            return self._handle_with_confirmation(raw_input, intent, params)

        # Execute immediately
        return self._execute(raw_input, intent, params)

    def _handle_with_confirmation(self, raw_input: str, intent: str, params: Dict[str, Any]) -> str:
        """Queues a high-risk action for confirmation."""
        desc = self._describe_action(intent, params)

        def on_confirm():
            result = self._execute(raw_input, intent, params)
            if self._on_response:
                self._on_response(result)

        def on_cancel():
            if self._on_response:
                self._on_response(f"Canceled: {desc}")

        confirmation_manager.request_confirmation(desc, on_confirm, on_cancel)

        if self._on_confirmation_needed:
            self._on_confirmation_needed(desc)

        return f"This action requires confirmation: {desc}. Say yes to confirm or no to cancel."

    def _describe_action(self, intent: str, params: Dict[str, Any]) -> str:
        desc_map = {
            "POWER_SHUTDOWN": "Shut down the PC",
            "POWER_RESTART": "Restart the PC",
            "POWER_SLEEP": "Put the PC to sleep",
            "POWER_LOCK": "Lock the PC",
            "DELETE_FILE": f"Delete file: {params.get('target', 'unknown')}",
        }
        return desc_map.get(intent, f"Execute {intent}")

    def _execute(self, raw_input: str, intent: str, params: Dict[str, Any]) -> str:
        """Executes the dispatched intent and returns a response string."""
        h = self._h()
        success, msg = False, "I'm not sure how to handle that."

        try:
            # ---- App Control ----
            if intent == "OPEN_APP":
                success, msg = h["app_launcher"].open_app(params.get("app_name", ""))

            elif intent == "CLOSE_APP":
                success, msg = h["app_launcher"].close_app(params.get("app_name", ""))

            # ---- Browser / Web ----
            elif intent == "SEARCH_WEB":
                engine = params.get("engine", "google")
                query = params.get("query", "")
                success, msg = h["web_handler"].search_web(query, engine)

            elif intent == "OPEN_WEBSITE":
                site = params.get("site", params.get("url", ""))
                success, msg = h["web_handler"].open_website(site)

            # ---- Files & Folders ----
            elif intent == "OPEN_FOLDER":
                folder = params.get("folder_name", params.get("target", ""))
                success, msg = h["folder_manager"].open_folder(folder)

            elif intent == "OPEN_FILE":
                target = params.get("target", "")
                success, found_files, _ = h["file_search_engine"].search(target)
                if success and found_files:
                    try:
                        os.startfile(str(found_files[0]))
                        conversation_manager.update_context("last_file", str(found_files[0]))
                        success, msg = True, f"Opening {found_files[0].name}."
                    except Exception as e:
                        success, msg = False, f"Could not open file: {e}"
                else:
                    success, msg = False, f"Could not find file '{target}'."

            elif intent == "SEARCH_FILE":
                query = params.get("query", "")
                success, found_files, msg = h["file_search_engine"].search(query)
                if success and found_files:
                    names = ", ".join(f.name for f in found_files[:3])
                    msg = f"Found {len(found_files)} file(s): {names}"

            elif intent == "CREATE_FOLDER":
                target = params.get("target", "NewFolder")
                try:
                    folder_path = Path.home() / "Desktop" / target
                    folder_path.mkdir(parents=True, exist_ok=True)
                    success, msg = True, f"Created folder '{target}' on your Desktop."
                except Exception as e:
                    success, msg = False, f"Could not create folder: {e}"

            elif intent == "CREATE_FILE":
                target = params.get("target", "new_file.txt")
                try:
                    file_path = Path.home() / "Desktop" / target
                    if not file_path.suffix:
                        file_path = file_path.with_suffix(".txt")
                    file_path.write_text("")
                    success, msg = True, f"Created file '{file_path.name}' on your Desktop."
                except Exception as e:
                    success, msg = False, f"Could not create file: {e}"

            elif intent == "DELETE_FILE":
                target = params.get("target", "")
                p = Path(target)
                if not p.exists():
                    # Look up in Desktop or Downloads
                    desk_p = Path.home() / "Desktop" / target
                    down_p = Path.home() / "Downloads" / target
                    if desk_p.exists():
                        p = desk_p
                    elif down_p.exists():
                        p = down_p
                try:
                    if p.exists():
                        if p.is_file():
                            p.unlink()
                        else:
                            import shutil
                            shutil.rmtree(str(p))
                        success, msg = True, f"Deleted '{p.name}'."
                    else:
                        success, msg = False, f"File '{target}' not found."
                except Exception as e:
                    success, msg = False, f"Could not delete: {e}"

            # ---- Screenshot ----
            elif intent == "SCREENSHOT":
                success, msg = h["screenshot_manager"].take_screenshot()

            # ---- Volume ----
            elif intent == "VOLUME_CONTROL":
                action = params.get("action", "increase")
                level = params.get("level")
                if level:
                    try:
                        level = int(level)
                    except:
                        level = None
                success, msg = h["volume_controller"].execute_action(action, level)

            # ---- Media Controls ----
            elif intent == "MEDIA_CONTROL":
                action = params.get("action", "playpause")
                success, msg = h["keyboard_controller"].media_control(action)

            # ---- System Info ----
            elif intent == "SYSTEM_INFO":
                info_type = params.get("type", "all")
                success, msg = h["system_monitor"].get_info(info_type)

            # ---- Window Control ----
            elif intent == "WINDOW_CONTROL":
                action = params.get("action", "minimize")
                app_name = params.get("app_name")
                success, msg = h["window_controller"].control_window(action, app_name)

            # ---- Power Commands ----
            elif intent == "POWER_CANCEL_SHUTDOWN":
                success, msg = h["power_manager"].cancel_shutdown()
            elif intent == "POWER_SHUTDOWN":
                success, msg = h["power_manager"].shutdown()
            elif intent == "POWER_RESTART":
                success, msg = h["power_manager"].restart()
            elif intent == "POWER_SLEEP":
                success, msg = h["power_manager"].sleep()
            elif intent == "POWER_LOCK":
                success, msg = h["power_manager"].lock()

            # ---- Keyboard ----
            elif intent == "KEYBOARD_ACTION":
                action = params.get("action", "")
                text = params.get("text", "")
                key = params.get("key", "")
                success, msg = h["keyboard_controller"].execute_action(action, text, key)

            # ---- Mouse ----
            elif intent == "MOUSE_ACTION":
                action = params.get("action", "click")
                success, msg = h["mouse_controller"].execute_action(action)

            # ---- AI Query ----
            elif intent == "AI_QUERY":
                query = params.get("query", raw_input)
                msg = gemini_client.query(query)
                success = True

            else:
                msg = gemini_client.query(raw_input)
                success = True

        except Exception as e:
            logger.error(f"Dispatcher error on '{intent}': {e}")
            msg = f"I encountered an error: {e}"
            success = False

        # Log to DB
        status = "SUCCESS" if success else "FAILED"
        db_manager.log_command(raw_input, intent, status, msg[:500])
        logger.info(f"[{intent}] {status}: {msg[:100]}")
        return msg


command_dispatcher = CommandDispatcher()
