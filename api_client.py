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
_system_prompt_cache: str = None

# Module-level Gemini client and chat session
_client_initialized = False
_chat_session = None
_current_screenshot_path: str = None


def _load_system_prompt() -> str:
      """
          Load and cache the system prompt from SCREEN_TUTOR_SYSTEM_PROMPT.md.

              Returns:
                      str: The system prompt text.

                          Raises:
                                  FileNotFoundError: If SCREEN_TUTOR_SYSTEM_PROMPT.md is not found.
                                      """
      global _system_prompt_cache
      if _system_prompt_cache is None:
                if not SYSTEM_PROMPT_PATH.exists():
                              raise FileNotFoundError(
                                                f"System prompt file not found: {SYSTEM_PROMPT_PATH}\n"
                                                "Please ensure SCREEN_TUTOR_SYSTEM_PROMPT.md exists in the project root."
                              )
                          _system_prompt_cache = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
                print(f"System prompt loaded from: {SYSTEM_PROMPT_PATH}")
            return _system_prompt_cache


def _initialize_client() -> None:
      """
          Initialize the Gemini API client using the GEMINI_API_KEY environment variable.

              Raises:
                      ValueError: If GEMINI_API_KEY is not set.
                          """
    global _client_initialized
    if not _client_initialized:
              api_key = os.environ.get("GEMINI_API_KEY")
              if not api_key:
                            raise ValueError(
                                              "GEMINI_API_KEY environment variable is not set.\n"
                                              "Please add your API key to the .env file."
                            )
                        genai.configure(api_key=api_key)
        _client_initialized = True
        print("Gemini API client initialized.")


def query_gemini(screenshot_path: str) -> str:
      """
          Send a screenshot to the Gemini API with the system prompt and get a tutoring response.
              This starts a new chat session with the screenshot as the initial context.

                  Args:
                          screenshot_path: Path to the screenshot image file.

                              Returns:
                                      str: The AI tutor's response text.

                                          Raises:
                                                  FileNotFoundError: If the screenshot file doesn't exist.
                                                          ValueError: If the API key is not configured.
                                                                  Exception: If the API call fails.
                                                                      """
    global _chat_session, _current_screenshot_path

    _initialize_client()
    system_prompt = _load_system_prompt()

    if not os.path.exists(screenshot_path):
              raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

    # Load the screenshot image
    image = Image.open(screenshot_path)
    _current_screenshot_path = screenshot_path

    # Create a new generative model with the system prompt
    model = genai.GenerativeModel(
              model_name=GEMINI_MODEL,
              system_instruction=system_prompt
    )

    # Start a new chat session
    _chat_session = model.start_chat(history=[])

    # Send the screenshot as the first message
    print(f"Sending screenshot to Gemini ({GEMINI_MODEL})...")
    response = _chat_session.send_message([
              image,
              "Please analyze this screenshot and provide tutoring assistance based on what you see."
    ])

    return response.text


def query_gemini_followup(user_message: str) -> str:
      """
          Send a follow-up chat message in the current session (screenshot stays in context).

              Args:
                      user_message: The user's follow-up question or message.

                          Returns:
                                  str: The AI tutor's response text.

                                      Raises:
                                              RuntimeError: If no active chat session exists (call query_gemini first).
                                                      Exception: If the API call fails.
                                                          """
    global _chat_session

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
