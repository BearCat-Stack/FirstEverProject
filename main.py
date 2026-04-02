"""
Codex AI Screen Tutor - Main Application
Listens for hotkey (ctrl+shift+s) to capture screen and query Gemini AI.
"""

import threading
import keyboard
from dotenv import load_dotenv

from screen_capture import capture_screenshot
from api_client import query_gemini
from ui import TutorOverlay

# Load environment variables from .env file
load_dotenv()


def main():
      """Main application entry point."""
      print("Codex AI Screen Tutor started.")
      print("Press Ctrl+Shift+S to capture your screen and get AI tutoring.")
      print("Press Ctrl+C or close the window to exit.\n")

    # Create the overlay UI (runs in its own thread via tkinter mainloop)
      overlay = TutorOverlay()

    def on_hotkey():
              """Callback when the hotkey is pressed."""
              print("Hotkey detected - capturing screen...")
              try:
                            # Capture screenshot
                            screenshot_path = capture_screenshot()
                            print(f"Screenshot saved to: {screenshot_path}")

                  # Show loading state in the overlay
                            overlay.show_loading()

                  # Query Gemini in a background thread to avoid blocking the hotkey listener
                            def query_and_display():
                                              try:
                                                                    response = query_gemini(screenshot_path)
                                                                    overlay.show_response(response, screenshot_path)
              except Exception as e:
                                    overlay.show_error(str(e))

                  thread = threading.Thread(target=query_and_display, daemon=True)
            thread.start()

except Exception as e:
            print(f"Error capturing screenshot: {e}")
            overlay.show_error(str(e))

    # Register the global hotkey
    keyboard.add_hotkey("ctrl+shift+s", on_hotkey)
    print("Hotkey registered: Ctrl+Shift+S")

    try:
              # Start the tkinter main loop (blocks until window is closed)
              overlay.run()
except KeyboardInterrupt:
        print("\nExiting Codex AI Screen Tutor...")
finally:
        keyboard.unhook_all()
        print("Goodbye!")


if __name__ == "__main__":
      main()
