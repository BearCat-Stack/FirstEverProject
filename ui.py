"""
Tkinter Overlay UI for Codex AI Screen Tutor.
Displays AI responses in a semi-transparent overlay window.
Includes a Capture button and chat input for follow-up questions.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from typing import Optional, Callable


class TutorOverlay:
    """A tkinter-based overlay window that displays AI tutor responses."""

    WINDOW_WIDTH = 520
    WINDOW_HEIGHT = 640
    WINDOW_ALPHA = 0.95
    BG_COLOR = "#1e1e2e"
    HEADER_COLOR = "#313244"
    TEXT_COLOR = "#cdd6f4"
    ACCENT_COLOR = "#89b4fa"
    ERROR_COLOR = "#f38ba8"
    LOADING_COLOR = "#a6e3a1"
    INPUT_BG = "#313244"
    BUTTON_COLOR = "#89b4fa"
    BUTTON_TEXT_COLOR = "#1e1e2e"
    CAPTURE_COLOR = "#a6e3a1"

    def __init__(self, on_capture: Optional[Callable] = None):
        """Initialize the overlay window."""
        self._root = tk.Tk()
        self._visible = True
        self._on_followup_callback: Optional[Callable] = None
        self._on_capture = on_capture
        self._setup_window()
        self._setup_widgets()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        root = self._root
        root.title("Codex AI Screen Tutor")
        root.configure(bg=self.BG_COLOR)
        try:
            root.attributes("-alpha", self.WINDOW_ALPHA)
            root.attributes("-topmost", True)
        except Exception:
            pass
        root.resizable(True, True)
        root.minsize(400, 300)

        try:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            x = max(0, screen_w - self.WINDOW_WIDTH - 20)
            y = max(0, screen_h - self.WINDOW_HEIGHT - 60)
            root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")
        except Exception:
            root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")

        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        """Handle window close."""
        self._visible = False
        self._root.destroy()

    def _setup_widgets(self) -> None:
        """Create and layout all UI widgets."""
        root = self._root

        # Header
        header_frame = tk.Frame(root, bg=self.HEADER_COLOR, pady=8)
        header_frame.pack(fill=tk.X, padx=0, pady=0)

        title_label = tk.Label(
            header_frame,
            text="Codex AI Screen Tutor",
            font=("Segoe UI", 12, "bold"),
            bg=self.HEADER_COLOR,
            fg=self.ACCENT_COLOR,
        )
        title_label.pack(side=tk.LEFT, padx=12)

        self._status_label = tk.Label(
            header_frame,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.HEADER_COLOR,
            fg="#6c7086",
        )
        self._status_label.pack(side=tk.RIGHT, padx=12)

        # Capture button bar
        capture_frame = tk.Frame(root, bg=self.BG_COLOR, pady=6)
        capture_frame.pack(fill=tk.X, padx=10)

        capture_btn = tk.Button(
            capture_frame,
            text="📸  Capture Screen & Analyze",
            font=("Segoe UI", 11, "bold"),
            bg=self.CAPTURE_COLOR,
            fg=self.BUTTON_TEXT_COLOR,
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._on_capture_click,
        )
        capture_btn.pack(fill=tk.X)

        hotkey_label = tk.Label(
            capture_frame,
            text="Shortcut: Ctrl+Shift+S  (requires root on Linux)",
            font=("Segoe UI", 8),
            bg=self.BG_COLOR,
            fg="#6c7086",
        )
        hotkey_label.pack(pady=(2, 0))

        # Separator
        ttk.Separator(root, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)

        # Response text area
        text_frame = tk.Frame(root, bg=self.BG_COLOR)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 0))

        self._response_text = scrolledtext.ScrolledText(
            text_frame,
            font=("Segoe UI", 10),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR,
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=8,
            pady=8,
            state=tk.DISABLED,
            insertbackground=self.TEXT_COLOR,
        )
        self._response_text.pack(fill=tk.BOTH, expand=True)

        # Separator
        ttk.Separator(root, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)

        # Chat input area
        chat_frame = tk.Frame(root, bg=self.BG_COLOR, pady=4)
        chat_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(
            chat_frame,
            text="Follow-up question:",
            font=("Segoe UI", 9),
            bg=self.BG_COLOR,
            fg="#6c7086",
        ).pack(anchor=tk.W)

        input_frame = tk.Frame(chat_frame, bg=self.BG_COLOR)
        input_frame.pack(fill=tk.X, pady=(2, 0))

        self._chat_input = tk.Entry(
            input_frame,
            font=("Segoe UI", 10),
            bg=self.INPUT_BG,
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.ACCENT_COLOR,
            highlightcolor=self.ACCENT_COLOR,
        )
        self._chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))
        self._chat_input.bind("<Return>", self._on_send)

        tk.Button(
            input_frame,
            text="Send",
            font=("Segoe UI", 10, "bold"),
            bg=self.BUTTON_COLOR,
            fg=self.BUTTON_TEXT_COLOR,
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._on_send,
        ).pack(side=tk.RIGHT)

        # Initial message
        self._set_response_text(
            "Welcome to Codex AI Screen Tutor!\n\n"
            "Click 'Capture Screen & Analyze' above to take a screenshot\n"
            "and get instant AI tutoring on what's on your screen.\n\n"
            "After a capture, use the chat box below for follow-up questions.",
            color="#6c7086"
        )

    def _on_capture_click(self) -> None:
        """Handle capture button click."""
        if self._on_capture:
            threading.Thread(target=self._on_capture, daemon=True).start()

    def _on_send(self, event=None) -> None:
        """Handle send button click or Enter key in chat input."""
        message = self._chat_input.get().strip()
        if not message:
            return

        self._chat_input.delete(0, tk.END)
        self._append_text(f"\nYou: {message}\n", color=self.ACCENT_COLOR)
        self._status_label.config(text="Thinking...", fg=self.LOADING_COLOR)

        if self._on_followup_callback:
            def run_callback():
                try:
                    response = self._on_followup_callback(message)
                    self._root.after(0, lambda: self._append_text(
                        f"\nAI: {response}\n", color=self.TEXT_COLOR
                    ))
                    self._root.after(0, lambda: self._status_label.config(
                        text="Done", fg=self.ACCENT_COLOR
                    ))
                except Exception as e:
                    self._root.after(0, lambda: self.show_error(str(e)))

            threading.Thread(target=run_callback, daemon=True).start()

    def _set_response_text(self, text: str, color: str = None) -> None:
        """Replace the full response text area content."""
        self._response_text.config(state=tk.NORMAL)
        self._response_text.delete("1.0", tk.END)
        if color:
            tag = "colored"
            self._response_text.tag_configure(tag, foreground=color)
            self._response_text.insert(tk.END, text, tag)
        else:
            self._response_text.insert(tk.END, text)
        self._response_text.config(state=tk.DISABLED)

    def _append_text(self, text: str, color: str = None) -> None:
        """Append text to the response area."""
        self._response_text.config(state=tk.NORMAL)
        if color:
            tag = f"tag_{len(self._response_text.tag_names())}"
            self._response_text.tag_configure(tag, foreground=color)
            self._response_text.insert(tk.END, text, tag)
        else:
            self._response_text.insert(tk.END, text)
        self._response_text.config(state=tk.DISABLED)
        self._response_text.see(tk.END)

    def show_loading(self) -> None:
        """Show a loading indicator in the overlay."""
        self._root.after(0, self._show_loading_main_thread)

    def _show_loading_main_thread(self) -> None:
        self._status_label.config(text="Analyzing screenshot...", fg=self.LOADING_COLOR)
        self._set_response_text("Analyzing your screen with Gemini AI...", color=self.LOADING_COLOR)

    def show_response(self, response_text: str, screenshot_path: str = None) -> None:
        """Display the AI response in the overlay."""
        self._root.after(0, lambda: self._show_response_main_thread(response_text))

    def _show_response_main_thread(self, response_text: str) -> None:
        self._status_label.config(text="Analysis complete ✓", fg=self.ACCENT_COLOR)
        self._set_response_text(response_text)
        try:
            from api_client import query_followup
            self._on_followup_callback = query_followup
        except ImportError:
            pass

    def show_error(self, error_message: str) -> None:
        """Display an error message in the overlay."""
        self._root.after(0, lambda: self._show_error_main_thread(error_message))

    def _show_error_main_thread(self, error_message: str) -> None:
        self._status_label.config(text="Error", fg=self.ERROR_COLOR)
        self._set_response_text(f"❌ Error: {error_message}", color=self.ERROR_COLOR)

    def hide(self) -> None:
        """Hide the overlay window."""
        self._root.withdraw()
        self._visible = False

    def is_visible(self) -> bool:
        return self._visible

    def run(self) -> None:
        """Start the tkinter event loop."""
        self._root.mainloop()
