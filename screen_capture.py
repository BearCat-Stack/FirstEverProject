"""
Screen Capture Module for Codex AI Screen Tutor.
Uses pyautogui to capture the full screen and save it as a temporary file.
"""

import os
import tempfile
from datetime import datetime
import pyautogui
from PIL import Image


def capture_screenshot(save_dir: str = None) -> str:
    """
    Capture a full screenshot of the primary screen.

    Args:
        save_dir: Optional directory to save the screenshot.
                  Defaults to a system temp directory.

    Returns:
        str: The absolute file path of the saved screenshot.

    Raises:
        OSError: If the screenshot cannot be saved to the specified directory.
    """
    if save_dir is None:
        save_dir = tempfile.gettempdir()

    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"codex_screenshot_{timestamp}.png"
    filepath = os.path.join(save_dir, filename)

    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)

    return filepath
