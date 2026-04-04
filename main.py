"""
Codex AI Screen Tutor - Main Application
Listens for hotkey (ctrl+shift+s) to capture screen and query Gemini AI.
"""

import threading
import sys
from dotenv import load_dotenv

from screen_capture import capture_screenshot
from api_client import query_gemini
from ui import TutorOverlay

# Load environment variables from .env file
load_dotenv()

# Try to import keyboard - requires root on Linux
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

_overlay = None


def trigger_capture():
    """Capture screen and display AI response. Can be called from hotkey or UI button."""
    global _overlay
    if _overlay is None:
        return
    print("Capturing screen...")
    try:
        screenshot_path = capture_screenshot()
        print(f"Screenshot saved to: {screenshot_path}")
        _overlay.show_loading()

        def query_and_display():
            try:
                response = query_gemini(screenshot_path)
                _overlay.show_response(response, screenshot_path)
            except Exception as e:
                _overlay.show_error(str(e))

        threading.Thread(target=query_and_display, daemon=True).start()

    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        _overlay.show_error(str(e))


def main():
    """Main application entry point."""
    global _overlay

    print("Codex AI Screen Tutor started.")
    print("Press Ctrl+C or close the window to exit.\n")

    # Create the overlay UI
    _overlay = TutorOverlay(on_capture=trigger_capture)

    # Register global hotkey if keyboard library is available
    if KEYBOARD_AVAILABLE:
        try:
            keyboard.add_hotkey("ctrl+shift+s", trigger_capture)
            print("Hotkey registered: Ctrl+Shift+S")
            print("Press Ctrl+Shift+S to capture your screen and get AI tutoring.")
        except Exception as e:
            print(f"Could not register hotkey: {e}")
            print("Use the 'Capture' button in the overlay window instead.")
    else:
        print("Note: Global hotkey unavailable (requires root on Linux).")
        print("Use the 'Capture' button in the overlay window instead.")

    try:
        _overlay.run()
    except KeyboardInterrupt:
        print("\nExiting Codex AI Screen Tutor...")
    finally:
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all()
            except Exception:
                pass
        print("Goodbye!")


if __name__ == "__main__":
    main()
