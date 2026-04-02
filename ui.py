"""
Tkinter Overlay UI for Codex AI Screen Tutor.
Displays AI responses in a semi-transparent overlay window.
Includes a chat input for follow-up questions.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from typing import Optional, Callable


class TutorOverlay:
      """
          A tkinter-based overlay window that displays AI tutor responses
              and provides a chat input for follow-up questions.
                  """

    # Window appearance constants
      WINDOW_WIDTH = 520
      WINDOW_HEIGHT = 600
      WINDOW_ALPHA = 0.92
      BG_COLOR = "#1e1e2e"
      HEADER_COLOR = "#313244"
      TEXT_COLOR = "#cdd6f4"
      ACCENT_COLOR = "#89b4fa"
      ERROR_COLOR = "#f38ba8"
      LOADING_COLOR = "#a6e3a1"
      INPUT_BG = "#313244"
      BUTTON_COLOR = "#89b4fa"
      BUTTON_TEXT_COLOR = "#1e1e2e"

    def __init__(self):
              """Initialize the overlay window."""
              self._root = tk.Tk()
              self._root.withdraw()  # Hide initially

        # State
              self._visible = False
              self._on_follow_up_callback: Optional[Callable[[str], None]] = None

        self._setup_window()
        self._setup_widgets()

    def _setup_window(self) -> None:
              """Configure the main window properties."""
              root = self._root
              root.title("Codex AI Screen Tutor")
              root.configure(bg=self.BG_COLOR)
              root.attributes("-alpha", self.WINDOW_ALPHA)
              root.attributes("-topmost", True)  # Always on top
        root.resizable(True, True)
        root.minsize(400, 300)

        # Position in the bottom-right corner of the screen
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = screen_w - self.WINDOW_WIDTH - 20
        y = screen_h - self.WINDOW_HEIGHT - 60
        root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")

        # Close button behavior: hide instead of destroy
        root.protocol("WM_DELETE_WINDOW", self.hide)

    def _setup_widgets(self) -> None:
              """Create and layout all UI widgets."""
              root = self._root

        # --- Header ---
              header_frame = tk.Frame(root, bg=self.HEADER_COLOR, pady=8)
              header_frame.pack(fill=tk.X, padx=0, pady=0)

        title_label = tk.Label(
                      header_frame,
                      text="Codex AI Screen Tutor",
                      font=("Segoe UI", 11, "bold"),
                      bg=self.HEADER_COLOR,
                      fg=self.ACCENT_COLOR
        )
        title_label.pack(side=tk.LEFT, padx=12)

        hint_label = tk.Label(
                      header_frame,
                      text="Ctrl+Shift+S to capture",
                      font=("Segoe UI", 9),
                      bg=self.HEADER_COLOR,
                      fg="#6c7086"
        )
        hint_label.pack(side=tk.LEFT, padx=4)

        close_btn = tk.Button(
                      header_frame,
                      text="X",
                      font=("Segoe UI", 9, "bold"),
                      bg=self.HEADER_COLOR,
                      fg="#6c7086",
                      bd=0,
                      cursor="hand2",
                      command=self.hide
        )
        close_btn.pack(side=tk.RIGHT, padx=8)

        # --- Response area ---
        response_frame = tk.Frame(root, bg=self.BG_COLOR)
        response_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6, 4))

        self._status_label = tk.Label(
                      response_frame,
                      text="Press Ctrl+Shift+S to analyze your screen",
                      font=("Segoe UI", 10),
                      bg=self.BG_COLOR,
                      fg="#6c7086",
                      wraplength=self.WINDOW_WIDTH - 40
        )
        self._status_label.pack(pady=(4, 2))

        self._response_text = scrolledtext.ScrolledText(
                      response_frame,
                      wrap=tk.WORD,
                      font=("Segoe UI", 10),
                      bg=self.INPUT_BG,
                      fg=self.TEXT_COLOR,
                      insertbackground=self.TEXT_COLOR,
                      relief=tk.FLAT,
                      state=tk.DISABLED,
                      pady=8,
                      padx=8
        )
        self._response_text.pack(fill=tk.BOTH, expand=True)

        # --- Separator ---
        separator = ttk.Separator(root, orient="horizontal")
        separator.pack(fill=tk.X, padx=10, pady=4)

        # --- Chat input area ---
        chat_frame = tk.Frame(root, bg=self.BG_COLOR, pady=4)
        chat_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        chat_label = tk.Label(
                      chat_frame,
                      text="Follow-up question:",
                      font=("Segoe UI", 9),
                      bg=self.BG_COLOR,
                      fg="#6c7086"
        )
        chat_label.pack(anchor=tk.W)

        input_frame = tk.Frame(chat_frame, bg=self.BG_COLOR)
        input_frame.pack(fill=tk.X, pady=(2, 0))

        self._chat_input = tk.Entry(
                      input_frame,
                      font=("Segoe UI", 10),
                      bg=self.INPUT_BG,
                      fg=self.TEXT_COLOR,
                      insertbackground=self.TEXT_COLOR,
                      relief=tk.FLAT,
                      bd=4
        )
        self._chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self._chat_input.bind("<Return>", self._on_send)

        self._send_btn = tk.Button(
                      input_frame,
                      text="Send",
                      font=("Segoe UI", 9, "bold"),
                      bg=self.BUTTON_COLOR,
                      fg=self.BUTTON_TEXT_COLOR,
                      relief=tk.FLAT,
                      cursor="hand2",
                      padx=10,
                      pady=4,
                      command=self._on_send
        )
        self._send_btn.pack(side=tk.RIGHT)

    def set_follow_up_callback(self, callback: Callable[[str], None]) -> None:
              """
                      Set a callback function to be called when the user submits a follow-up question.

                              Args:
                                          callback: Function that receives the user's follow-up text.
                                                  """
              self._on_follow_up_callback = callback

    def _on_send(self, event=None) -> None:
              """Handle the send button click or Enter key press."""
              message = self._chat_input.get().strip()
              if not message:
                            return

              if self._on_follow_up_callback is None:
                            self._show_text_threadsafe(
                                              "No follow-up handler configured. Please capture a screenshot first.",
                                              color=self.ERROR_COLOR
                            )
                            return

              # Clear input and show the user's message
              self._chat_input.delete(0, tk.END)
        self._append_text_threadsafe(f"\n\nYou: {message}\n", color=self.ACCENT_COLOR)
        self._status_label.config(text="Thinking...", fg=self.LOADING_COLOR)

        # Run the callback in a background thread
        def run_callback():
                      try:
                                        self._on_follow_up_callback(message)
except Exception as e:
                self.show_error(str(e))

        threading.Thread(target=run_callback, daemon=True).start()

    def show_loading(self) -> None:
              """Show a loading indicator in the overlay."""
              self._root.after(0, self._show_loading_main_thread)

    def _show_loading_main_thread(self) -> None:
              """Internal: called on the main thread to show loading state."""
              self._root.deiconify()
              self._visible = True
              self._status_label.config(text="Analyzing screenshot...", fg=self.LOADING_COLOR)
              self._set_response_text("Analyzing your screen with Gemini AI...")
              self._root.lift()

    def show_response(self, response_text: str, screenshot_path: str = None) -> None:
              """
                      Display the AI response in the overlay.

                              Args:
                                          response_text: The AI tutor's response to display.
                                                      screenshot_path: Optional path to the screenshot (for context display).
                                                              """
              self._root.after(0, lambda: self._show_response_main_thread(response_text, screenshot_path))

    def _show_response_main_thread(self, response_text: str, screenshot_path: str) -> None:
              """Internal: called on the main thread to update the response."""
              self._status_label.config(text="AI Response", fg=self.ACCENT_COLOR)
              self._set_response_text(response_text)
              self._root.deiconify()
              self._visible = True
              self._root.lift()

        # Set up follow-up handler
              def handle_followup(user_message: str):
                            from api_client import query_gemini_followup
                            try:
                                              follow_response = query_gemini_followup(user_message)
                                              self._root.after(0, lambda: self._append_follow_up_response(follow_response))
except Exception as e:
                self.show_error(str(e))

        self.set_follow_up_callback(handle_followup)

    def _append_follow_up_response(self, response_text: str) -> None:
              """Append a follow-up response to the text area."""
              self._status_label.config(text="AI Response", fg=self.ACCENT_COLOR)
              self._append_text_threadsafe(f"\nAI Tutor: {response_text}\n", color=self.TEXT_COLOR)

    def show_error(self, error_message: str) -> None:
              """Display an error message in the overlay."""
              self._root.after(0, lambda: self._show_error_main_thread(error_message))

    def _show_error_main_thread(self, error_message: str) -> None:
              """Internal: called on the main thread to show an error."""
              self._status_label.config(text="Error", fg=self.ERROR_COLOR)
              self._set_response_text(f"Error: {error_message}")
              self._root.deiconify()
              self._visible = True

    def _set_response_text(self, text: str) -> None:
              """Replace the content of the response text area."""
              self._response_text.config(state=tk.NORMAL)
              self._response_text.delete("1.0", tk.END)
              self._response_text.insert(tk.END, text)
              self._response_text.config(state=tk.DISABLED)
              self._response_text.see(tk.END)

    def _show_text_threadsafe(self, text: str, color: str = None) -> None:
              """Thread-safe method to update the response text."""
              self._root.after(0, lambda: self._set_response_text(text))

    def _append_text_threadsafe(self, text: str, color: str = None) -> None:
              """Thread-safe method to append text to the response area."""
              def _append():
                            self._response_text.config(state=tk.NORMAL)
                            self._response_text.insert(tk.END, text)
                            self._response_text.config(state=tk.DISABLED)
                            self._response_text.see(tk.END)
                        self._root.after(0, _append)

    def hide(self) -> None:
              """Hide the overlay window."""
        self._root.withdraw()
        self._visible = False

    def run(self) -> None:
              """Start the tkinter main loop. Blocks until the window is closed."""
        self._root.mainloop()

    @property
    def is_visible(self) -> bool:
              """Return True if the overlay is currently visible."""
        return self._visible


if __name__ == "__main__":
      # Quick UI test
      import time

    overlay = TutorOverlay()

    def test_sequence():
              time.sleep(1)
        overlay.show_loading()
        time.sleep(2)
        overlay.show_response(
                      "I can see a Python file open in your editor. "
                      "The code appears to be a tkinter UI implementation. "
                      "Would you like me to explain any specific part of the code?",
                      screenshot_path=None
        )

    t = threading.Thread(target=test_sequence, daemon=True)
    t.start()
    overlay.run()
