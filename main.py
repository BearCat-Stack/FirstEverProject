"""
Codex AI Screen Tutor - Main Entry Point
Captures screen, sends to Gemini AI, displays response in overlay.
"""

import threading
import time

# Try pynput first (works on Windows without admin), then keyboard as fallback
HOTKEY_AVAILABLE = False
HOTKEY_LIB = None

try:
    from pynput import keyboard as pynput_keyboard
    HOTKEY_AVAILABLE = True
    HOTKEY_LIB = "pynput"
except ImportError:
    pass

if not HOTKEY_AVAILABLE:
    try:
        import keyboard
        HOTKEY_AVAILABLE = True
        HOTKEY_LIB = "keyboard"
    except (ImportError, Exception):
        pass

from screen_capture import capture_screenshot
from api_client import query_gemini, query_followup
from ui import TutorOverlay


def main():
    """Main application entry point."""
    print("Starting Codex AI Screen Tutor...")

    # Shared state
    is_processing = False
    overlay = None

    def trigger_capture():
        """Capture screen and display AI response."""
        nonlocal is_processing
        if is_processing:
            print("Already processing, please wait...")
            return
        is_processing = True

        def _do_capture():
            nonlocal is_processing
            try:
                if overlay:
                    overlay.set_status("Capturing...")
                    overlay.update_response("Capturing screen...")

                time.sleep(0.3)

                # Capture screen - returns filepath string
                screenshot_path = capture_screenshot()

                if overlay:
                    overlay.set_status("Analyzing...")
                    overlay.update_response("Sending to Gemini AI...")

                # Get AI response
                response = query_gemini(screenshot_path)

                if overlay:
                    overlay.set_status("Ready")
                    overlay.update_response(response)

            except Exception as e:
                print(f"Error during capture: {e}")
                if overlay:
                    overlay.set_status("Error")
                    overlay.update_response(f"Error: {e}")
            finally:
                is_processing = False

        thread = threading.Thread(target=_do_capture, daemon=True)
        thread.start()

    # Create UI
    overlay = TutorOverlay(on_capture=trigger_capture)

    # Register global hotkey
    if HOTKEY_LIB == "pynput":
        try:
            current_keys = set()

            def on_press(key):
                current_keys.add(key)
                if (pynput_keyboard.Key.ctrl_l in current_keys or pynput_keyboard.Key.ctrl_r in current_keys or pynput_keyboard.Key.ctrl in current_keys) and \
                   (pynput_keyboard.Key.shift in current_keys or pynput_keyboard.Key.shift_l in current_keys or pynput_keyboard.Key.shift_r in current_keys) and \
                   (pynput_keyboard.KeyCode(char='s') in current_keys or pynput_keyboard.KeyCode(char='S') in current_keys):
                    trigger_capture()

            def on_release(key):
                current_keys.discard(key)

            listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
            listener.daemon = True
            listener.start()
            print("Global hotkey Ctrl+Shift+S registered (via pynput).")
        except Exception as e:
            print(f"Could not register hotkey via pynput: {e}")
            print("Use the 'Capture' button in the overlay window instead.")

    elif HOTKEY_LIB == "keyboard":
        try:
            keyboard.add_hotkey("ctrl+shift+s", trigger_capture)
            print("Global hotkey Ctrl+Shift+S registered (via keyboard).")
        except Exception as e:
            print(f"Could not register hotkey: {e}")
            print("Use the 'Capture' button in the overlay window instead.")
    else:
        print("No hotkey library available. Use the 'Capture' button in the overlay window.")

    print("Codex AI Screen Tutor started.")
    print("Press Ctrl+Shift+S anywhere or click the Capture button to analyze your screen.")
    print("Press Ctrl+C or close the window to exit.")

    try:
        overlay.run()
    except KeyboardInterrupt:
        print("\nExiting Codex AI Screen Tutor...")
    finally:
        if HOTKEY_LIB == "keyboard":
            try:
                keyboard.unhook_all()
            except Exception:
                pass
        print("Goodbye!")


if __name__ == "__main__":
    main()
