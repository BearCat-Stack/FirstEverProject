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

      # Ensure the save directory exists
      os.makedirs(save_dir, exist_ok=True)

    # Generate a timestamped filename
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
      filename = f"screen_tutor_{timestamp}.png"
      filepath = os.path.join(save_dir, filename)

    # Capture the screenshot using pyautogui
      screenshot = pyautogui.screenshot()

    # Save as PNG
      screenshot.save(filepath, format="PNG")

    return filepath


def get_screenshot_as_bytes(filepath: str) -> bytes:
      """
          Read a screenshot file and return its raw bytes.

              Args:
                      filepath: Path to the screenshot file.

                          Returns:
                                  bytes: The raw image data.
                                      """
      with open(filepath, "rb") as f:
                return f.read()


def cleanup_screenshot(filepath: str) -> None:
      """
          Delete a screenshot file to free up disk space.

              Args:
                      filepath: Path to the screenshot file to delete.
                          """
      try:
                if os.path.exists(filepath):
                              os.remove(filepath)
      except OSError as e:
                print(f"Warning: Could not delete screenshot {filepath}: {e}")


if __name__ == "__main__":
      # Quick test
      path = capture_screenshot()
      print(f"Screenshot captured: {path}")
      img = Image.open(path)
      print(f"Image size: {img.size}, mode: {img.mode}")
