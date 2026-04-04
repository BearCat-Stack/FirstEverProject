"""
Gemini API client for Codex AI Screen Tutor.
Handles sending screenshots and follow-up messages to the Gemini AI model.
"""

import os
import warnings
import concurrent.futures
from pathlib import Path

# Suppress the deprecation warning for google.generativeai
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Module-level state
_client_initialized = False
_model = None
_chat_session = None

# Timeout for API calls in seconds
API_TIMEOUT = 30


def _load_system_prompt() -> str:
    """Load the system prompt from the markdown file."""
    prompt_path = Path(__file__).parent / "SCREEN_TUTOR_SYSTEM_PROMPT.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "You are a helpful AI tutor. Analyze the screenshot and provide guidance."


def _initialize_client() -> None:
    """Initialize the Gemini API client."""
    global _client_initialized, _model

    if _client_initialized:
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please create a .env file with your API key."
        )

    genai.configure(api_key=api_key)
    _model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=_load_system_prompt()
    )
    _client_initialized = True


def query_gemini(screenshot_path: str) -> str:
    """
    Send a screenshot to Gemini and get an AI tutor response.
    Times out after 30 seconds to prevent hanging.

    Args:
        screenshot_path: Path to the screenshot image file.

    Returns:
        str: The AI tutor's response text.
    """
    global _chat_session

    _initialize_client()

    image = Image.open(screenshot_path)

    def _call_api():
        global _chat_session
        _chat_session = _model.start_chat()
        response = _chat_session.send_message([
            "Please analyze this screenshot and provide tutoring assistance.",
            image,
        ])
        return response.text

    # Run with timeout
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_call_api)
        try:
            result = future.result(timeout=API_TIMEOUT)
            return result
        except concurrent.futures.TimeoutError:
            _chat_session = None
            return f"Request timed out after {API_TIMEOUT} seconds. Please try again."
        except Exception as e:
            _chat_session = None
            error_msg = str(e)
            if "API_KEY" in error_msg.upper() or "401" in error_msg or "403" in error_msg:
                return "API key error. Please check your GEMINI_API_KEY in the .env file."
            elif "429" in error_msg:
                return "Rate limit reached. Please wait a moment and try again."
            elif "quota" in error_msg.lower():
                return "API quota exceeded. Please check your Gemini API usage."
            else:
                return f"Error communicating with Gemini: {error_msg}"


def query_followup(user_message: str) -> str:
    """
    Send a follow-up message in the existing chat session.
    Times out after 30 seconds.

    Args:
        user_message: The user's follow-up question.

    Returns:
        str: The AI tutor's response text.
    """
    if _chat_session is None:
        raise RuntimeError(
            "No active chat session. Please capture a screenshot first (Ctrl+Shift+S)."
        )

    def _call_api():
        response = _chat_session.send_message(user_message)
        return response.text

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_call_api)
        try:
            result = future.result(timeout=API_TIMEOUT)
            return result
        except concurrent.futures.TimeoutError:
            return f"Request timed out after {API_TIMEOUT} seconds. Please try again."
        except Exception as e:
            return f"Error: {e}"


def has_active_session() -> bool:
    """Check if there is an active chat session with a screenshot in context."""
    return _chat_session is not None
