"""
Gemini API Client for Codex AI Screen Tutor.
Handles communication with Google's Gemini API (gemini-2.0-flash with vision).
Loads the system prompt from SCREEN_TUTOR_SYSTEM_PROMPT.md.
"""

import os
import pathlib
import google.generativeai as genai
from PIL import Image

# Path to the system prompt file (relative to this script's location)
_SCRIPT_DIR = pathlib.Path(__file__).parent
SYSTEM_PROMPT_PATH = _SCRIPT_DIR / "SCREEN_TUTOR_SYSTEM_PROMPT.md"

# Gemini model to use
GEMINI_MODEL = "gemini-2.0-flash"

# Module-level cache for the loaded system prompt
_system_prompt_cache = None

# Module-level Gemini client and chat session
_client_initialized = False
_chat_session = None
_current_screenshot_path = None


def _load_system_prompt() -> str:
    """Load and cache the system prompt from SCREEN_TUTOR_SYSTEM_PROMPT.md."""
    global _system_prompt_cache
    if _system_prompt_cache is not None:
        return _system_prompt_cache

    if not SYSTEM_PROMPT_PATH.exists():
        _system_prompt_cache = (
            "You are a helpful AI tutor. Analyze the screenshot and provide guidance."
        )
    else:
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            _system_prompt_cache = f.read()

    return _system_prompt_cache


def _initialize_client() -> None:
    """Initialize the Gemini client with the API key."""
    global _client_initialized
    if _client_initialized:
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please create a .env file with your API key."
        )

    genai.configure(api_key=api_key)
    _client_initialized = True


def query_gemini(screenshot_path: str) -> str:
    """
    Send a screenshot to Gemini and get an AI tutor response.

    Args:
        screenshot_path: Path to the screenshot image file.

    Returns:
        str: The AI tutor's response text.
    """
    global _chat_session, _current_screenshot_path

    _initialize_client()
    system_prompt = _load_system_prompt()

    if not os.path.exists(screenshot_path):
        raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

    image = Image.open(screenshot_path)
    _current_screenshot_path = screenshot_path

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system_prompt,
    )
    _chat_session = model.start_chat()
    response = _chat_session.send_message([
        "Please analyze this screenshot and provide tutoring assistance.",
        image,
    ])
    return response.text


def query_followup(user_message: str) -> str:
    """
    Send a follow-up message in the existing chat session.

    Args:
        user_message: The user's follow-up question.

    Returns:
        str: The AI tutor's response text.
    """
    if _chat_session is None:
        raise RuntimeError(
            "No active chat session. Please capture a screenshot first (Ctrl+Shift+S)."
        )

    print(f"Sending follow-up message to Gemini...")
    response = _chat_session.send_message(user_message)
    return response.text


def has_active_session() -> bool:
    """Check if there is an active chat session with a screenshot in context."""
    return _chat_session is not None
