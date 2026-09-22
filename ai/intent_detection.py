import re
import json
from typing import Dict, Any, Tuple
from ai.gemini import gemini_client
from ai.prompts import INTENT_PARSER_PROMPT
from utils.logger import logger

class IntentDetector:
    """Hybrid intent classification engine using regex rules + Gemini fallback."""

    def __init__(self):
        # Regular expressions for direct local voice commands
        self.rules = [
            # Power Commands
            (r'^(?:cancel\s+shutdown|abort\s+shutdown|stop\s+shutdown)$', 'POWER_CANCEL_SHUTDOWN', {}),
            (r'^(shut\s*down|power\s*off)\s*(the\s*pc|the\s*computer|my\s*pc)?$', 'POWER_SHUTDOWN', {'action': 'shutdown'}),
            (r'^(restart|reboot)\s*(the\s*pc|the\s*computer|my\s*pc)?$', 'POWER_RESTART', {'action': 'restart'}),
            (r'^(sleep|hibernate)\s*(the\s*pc|the\s*computer|my\s*pc)?$', 'POWER_SLEEP', {'action': 'sleep'}),
            (r'^(lock|lock\s*pc|lock\s*my\s*pc)$', 'POWER_LOCK', {'action': 'lock'}),

            # Media & Music Controls
            (r'^(?:play\s+music|resume\s+music|play|pause|pause\s+music|toggle\s+playback)$', 'MEDIA_CONTROL', {'action': 'playpause'}),
            (r'^(?:next\s+track|next\s+song|skip\s+song|skip\s+track|next)$', 'MEDIA_CONTROL', {'action': 'nexttrack'}),
            (r'^(?:previous\s+track|previous\s+song|prev\s+song|previous|prev)$', 'MEDIA_CONTROL', {'action': 'prevtrack'}),

            # Volume Control
            (r'^(?:increase|raise|turn\s+up)\s+(?:the\s+)?volume$', 'VOLUME_CONTROL', {'action': 'increase'}),
            (r'^(?:decrease|lower|turn\s+down)\s+(?:the\s+)?volume$', 'VOLUME_CONTROL', {'action': 'decrease'}),
            (r'^mute(?:\s+volume|\s+audio)?$', 'VOLUME_CONTROL', {'action': 'mute'}),
            (r'^unmute(?:\s+volume|\s+audio)?$', 'VOLUME_CONTROL', {'action': 'unmute'}),
            (r'^(?:set\s+volume\s+to|volume)\s+(\d+)\s*(?:percent|%)?$', 'VOLUME_CONTROL', {'action': 'set'}),

            # Window Control
            (r'^(?:minimize|hide)\s+(?:this|the|active)?\s*window$', 'WINDOW_CONTROL', {'action': 'minimize'}),
            (r'^(?:maximize|expand)\s+(?:this|the|active)?\s*window$', 'WINDOW_CONTROL', {'action': 'maximize'}),
            (r'^(?:restore|unmaximize)\s+(?:this|the|active)?\s*window$', 'WINDOW_CONTROL', {'action': 'restore'}),
            (r'^(?:close)\s+(?:this|the|active)?\s*window$', 'WINDOW_CONTROL', {'action': 'close'}),
            (r'^(?:switch\s+to|show)\s+(?:the\s+)?(.+?)\s+window$', 'WINDOW_CONTROL', {'action': 'switch'}),

            # App Launcher & Control
            (r'^(?:can\s+you\s+)?(?:open|launch|start|run|show)\s+(?:the\s+)?(?:app\s+)?(.+?)(?:\s+app|\s+please)?$', 'OPEN_APP', None),
            (r'^(?:close|quit|exit|kill|stop)\s+(?:the\s+)?(.+?)(?:\s+app|\s+please)?$', 'CLOSE_APP', None),

            # Folder & File Access
            (r'^(?:open|show)\s+(?:my\s+)?(downloads|desktop|documents|pictures|photos|videos|music|projects?|project\s+folder|screenshots?)$', 'OPEN_FOLDER', None),
            (r'^(?:open|view|read)\s+(?:the\s+)?(?:file|document)\s+(.+)$', 'OPEN_FILE', None),
            (r'^(?:find|search\s+for|look\s+for)\s+(?:the\s+)?(?:file\s+)?(.+)$', 'SEARCH_FILE', None),
            (r'^(?:create|make)\s+a?\s*folder\s+(?:called|named)\s+(.+)$', 'CREATE_FOLDER', None),
            (r'^(?:create|make)\s+a?\s*(?:text\s+)?file\s+(?:called|named)\s+(.+)$', 'CREATE_FILE', None),
            (r'^(?:delete|remove)\s+(?:the\s+)?(?:file|folder)?\s*(.+)$', 'DELETE_FILE', None),

            # Browser & Web Search
            (r'^(?:search\s+youtube\s+for|find\s+on\s+youtube|play\s+on\s+youtube)\s+(.+)$', 'SEARCH_WEB', {'engine': 'youtube'}),
            (r'^(?:search\s+google\s+for|google)\s+(.+)$', 'SEARCH_WEB', {'engine': 'google'}),
            (r'^(?:search\s+bing\s+for|bing)\s+(.+)$', 'SEARCH_WEB', {'engine': 'bing'}),
            (r'^(?:search\s+duckduckgo\s+for|duckduckgo)\s+(.+)$', 'SEARCH_WEB', {'engine': 'duckduckgo'}),
            (r'^(?:search\s+(?:the\s+)?web\s+for|search\s+for)\s+(.+)$', 'SEARCH_WEB', {'engine': 'google'}),
            (r'^(?:open|go\s+to)\s+(google|youtube|github|gmail|wikipedia|reddit|twitter|x\.com|chatgpt|spotify|netflix|linkedin|stackoverflow)\.?(com|org)?$', 'OPEN_WEBSITE', None),

            # Screenshot
            (r'^(?:take\s+a?\s*)?screenshot|capture\s+(?:the\s+)?screen$', 'SCREENSHOT', {}),

            # System Information
            (r'^(?:show|get|check)\s+(?:my\s+)?(?:cpu|processor)(?:\s+usage|\s+status)?$', 'SYSTEM_INFO', {'type': 'cpu'}),
            (r'^(?:show|get|check)\s+(?:my\s+)?(?:ram|memory)(?:\s+usage|\s+status)?$', 'SYSTEM_INFO', {'type': 'ram'}),
            (r'^(?:show|get|check)\s+(?:my\s+)?battery(?:\s+status|\s+level)?$', 'SYSTEM_INFO', {'type': 'battery'}),
            (r'^(?:show|get|check)\s+(?:my\s+)?disk(?:\s+usage|\s+space)?$', 'SYSTEM_INFO', {'type': 'disk'}),
            (r'^(?:show|get|check)\s+(?:my\s+)?(?:ip|ip\s+address|network|wifi)$', 'SYSTEM_INFO', {'type': 'network'}),
            (r'^(?:show|get|check)\s+(?:my\s+)?(?:system\s+info|system\s+information|specs)$', 'SYSTEM_INFO', {'type': 'all'}),
            (r'^(?:what\s+time\s+is\s+it|what\s+is\s+the\s+time|current\s+time|time)$', 'SYSTEM_INFO', {'type': 'time'}),
            (r'^(?:what\s+is\s+the\s+date|what\s+is\s+today|today\'?s\s+date|date)$', 'SYSTEM_INFO', {'type': 'date'}),

            # Keyboard Automation
            (r'^type\s+(.+)$', 'KEYBOARD_ACTION', {'action': 'type'}),
            (r'^press\s+(enter|escape|backspace|tab|space|delete|up|down|left|right)$', 'KEYBOARD_ACTION', {'action': 'press'}),
            (r'^(?:copy|press\s+ctrl\s+c)$', 'KEYBOARD_ACTION', {'action': 'copy'}),
            (r'^(?:paste|press\s+ctrl\s+v)$', 'KEYBOARD_ACTION', {'action': 'paste'}),
            (r'^(?:select\s+all|press\s+ctrl\s+a)$', 'KEYBOARD_ACTION', {'action': 'select_all'}),
            (r'^scroll\s+down(?:\s+(\d+))?$', 'KEYBOARD_ACTION', {'action': 'scroll_down'}),
            (r'^scroll\s+up(?:\s+(\d+))?$', 'KEYBOARD_ACTION', {'action': 'scroll_up'}),

            # Mouse Automation
            (r'^(?:right\s+click|secondary\s+click)$', 'MOUSE_ACTION', {'action': 'right_click'}),
            (r'^(?:double\s+click)$', 'MOUSE_ACTION', {'action': 'double_click'}),
            (r'^(?:click|left\s+click)$', 'MOUSE_ACTION', {'action': 'click'}),
        ]

    def detect(self, raw_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        Detects intent and extracts parameters.
        Returns: (intent_name, params_dict)
        """
        cleaned = raw_input.strip().lower()
        if not cleaned:
            return "UNKNOWN", {}

        # Strip common prefix noise like "hey machi", "machi", "bro", "yo", "please", "can you"
        cleaned = re.sub(r'^(?:hey\s+machi|machi|ok\s+machi|hi\s+machi|yo\s+machi|bro|yo|please|can\s+you)\s*,?\s*', '', cleaned)
        cleaned = re.sub(r'\s*,?\s*please$', '', cleaned).strip()

        # 1. Check Regex Rule Engine First
        for pattern, intent, default_params in self.rules:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                params = default_params.copy() if default_params else {}
                groups = match.groups()
                if groups:
                    if intent in ["OPEN_APP", "CLOSE_APP"]:
                        params["app_name"] = groups[0].strip()
                    elif intent == "OPEN_FOLDER":
                        params["folder_name"] = groups[0].strip()
                    elif intent == "OPEN_FILE":
                        params["target"] = groups[0].strip()
                    elif intent == "SEARCH_FILE":
                        params["query"] = groups[0].strip()
                    elif intent == "SEARCH_WEB":
                        params["query"] = groups[0].strip()
                    elif intent == "OPEN_WEBSITE":
                        params["site"] = groups[0].strip()
                    elif intent in ["CREATE_FOLDER", "CREATE_FILE", "DELETE_FILE"]:
                        params["target"] = groups[0].strip()
                    elif intent == "VOLUME_CONTROL" and "level" not in params and groups[0]:
                        params["level"] = groups[0]
                    elif intent == "KEYBOARD_ACTION" and params.get("action") == "type":
                        params["text"] = groups[0]
                    elif intent == "KEYBOARD_ACTION" and params.get("action") == "press":
                        params["key"] = groups[0]
                    elif intent == "WINDOW_CONTROL" and params.get("action") == "switch":
                        params["app_name"] = groups[0]

                logger.info(f"Intent matched by regex: '{intent}' with params {params}")
                return intent, params

        # 2. General AI query fallback
        return "AI_QUERY", {"query": raw_input}

intent_detector = IntentDetector()
