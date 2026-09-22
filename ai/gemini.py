import os
import datetime
import platform
import random
from typing import Optional
from config import GEMINI_API_KEY, ASSISTANT_NAME
from ai.prompts import SYSTEM_ASSISTANT_PROMPT
from utils.logger import logger

try:
    import google.generativeai as genai
    GENAI_LIB_AVAILABLE = True
except ImportError:
    GENAI_LIB_AVAILABLE = False


class GeminiClient:
    """Wrapper around Google Gemini API with robust offline intelligence fallback."""

    def __init__(self):
        self.api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.model = None
        self._is_available = False
        self.model_candidates = [
            "gemini-2.5-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.5-flash",
            "gemini-flash-latest"
        ]

        if GENAI_LIB_AVAILABLE and self.api_key and len(self.api_key.strip()) > 10:
            self._init_api()
        else:
            logger.info("Gemini API key not configured or unavailable. Offline AI mode enabled.")

    def _init_api(self):
        try:
            genai.configure(api_key=self.api_key.strip())
            for model_name in self.model_candidates:
                try:
                    self.model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=SYSTEM_ASSISTANT_PROMPT
                    )
                    self._is_available = True
                    logger.info(f"Gemini API configured with model: {model_name}")
                    return
                except Exception:
                    continue
            self._is_available = False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self._is_available = False

    def is_available(self) -> bool:
        return self._is_available

    def query(self, prompt: str) -> str:
        """Sends a query to Gemini, falling back to smart local intelligence if unavailable."""
        if self._is_available and self.model:
            try:
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.debug(f"Gemini API query failed: {e}. Using offline intelligent responder.")

        # Offline Local Intelligent Fallback
        return self._offline_response(prompt)

    def _offline_response(self, query: str) -> str:
        """Provides instant, helpful responses locally for general queries and assistant chat."""
        q = query.lower().strip()
        now = datetime.datetime.now()

        # Greetings
        if any(w in q for w in ["hello", "hi", "hey", "good morning", "good evening", "good afternoon", "wassup", "what's up"]):
            greetings = [
                f"Hey! I'm {ASSISTANT_NAME}, your AI assistant. How can I help you with your laptop today?",
                f"Hello! {ASSISTANT_NAME} is here and ready. What would you like me to do?",
                f"Hey bro! Everything is running smoothly. How can I assist you?"
            ]
            return random.choice(greetings)

        # Time & Date
        if "time" in q:
            return f"It is currently {now.strftime('%I:%M %p')}."
        if "date" in q or "day" in q:
            return f"Today is {now.strftime('%A, %B %d, %Y')}."

        # Identity & Capabilities
        if "who are you" in q or "what is your name" in q or "what are you" in q:
            return f"I am {ASSISTANT_NAME}, your AI voice control desktop assistant. I can launch apps, search files, control windows, adjust volume, take screenshots, manage system power, and search the web."

        if "what can you do" in q or "help" in q or "commands" in q:
            return "I can control your laptop! Try saying: 'Open Chrome', 'Increase volume', 'Take screenshot', 'Search Google for Python tutorials', 'Show CPU usage', or 'Lock PC'."

        # System / Status
        if "how are you" in q or "how's it going" in q:
            return f"I'm running at peak performance and ready for your commands!"

        # Jokes
        if "joke" in q or "tell me a joke" in q:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "Why was the computer cold? Because it left its Windows open!",
                "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'"
            ]
            return random.choice(jokes)

        # Simple Math calculation
        import re
        math_match = re.search(r'(?:calculate|what is|how much is)?\s*(\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(\d+(?:\.\d+)?)', q)
        if math_match:
            n1, op, n2 = float(math_match.group(1)), math_match.group(2), float(math_match.group(3))
            if op == '+': res = n1 + n2
            elif op == '-': res = n1 - n2
            elif op == '*': res = n1 * n2
            elif op == '/': res = n1 / n2 if n2 != 0 else "undefined (cannot divide by zero)"
            return f"The answer is {res}."

        return f"I understand you're asking about '{query}'. You can command me to open apps, control volume, search files, or interact with your system."


gemini_client = GeminiClient()
