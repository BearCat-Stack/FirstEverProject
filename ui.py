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
    """A tkinter-based overlay window that displays AI tutor responses."""

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
        self._root.withdraw()
        self._visible = False
        self._on_followup_callback: Optional[Callable] = None
        self._setup_window()
        self._setup_widgets()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        root = self._root
        root.title("Codex AI Screen Tutor")
        root.configure(bg=self.BG_COLOR)
        root.attributes("-alpha", self.WINDOW_ALPHA)
        root.attributes("-topmost", True)
        root.resizable(True, True)
        root.minsize(400, 300)

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = screen_w - self.WINDOW_WIDTH - 20
        y = screen_h - self.WINDOW_HEIGHT - 60
        root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")

        root.protocol("WM_DELETE_WINDOW", self.hide)

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
            text="Ready  |  Press Ctrl+Shift+S to capture",
            font=("Segoe UI", 9),
            bg=self.HEADER_COLOR,
            fg="#6c7086",
        )
        self._status_label.pack(side=tk.RIGHT, padx=12)

        # Response text area
        text_frame = tk.Frame(root, bg=self.BG_COLOR)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(8, 0))

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
        separator = ttk.Separator(root, orient="horizontal")
        separator.pack(fill=tk.X, padx=10, pady=4)

        # Chat input area
        chat_frame = tk.Frame(root, bg=self.BG_COLOR, pady=4)
        chat_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        chat_label = tk.Label(
            chat_frame,
            text="Follow-up question:",
            font=("Segoe UI", 9),
            bg=self.BG_COLOR,
            fg="#6c7086",
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
            highlightthickness=1,
            highlightbackground=self.ACCENT_COLOR,
            highlightcolor=self.ACCENT_COLOR,
        )
        self._chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))
        self._chat_input.bind("<Return>", self._on_send)

        send_btn = tk.Button(
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
        )
        send_btn.pack(side=tk.RIGHT)

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
        self._response_text.see(tk.END)

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
        """Internal: called on the main thread to show loading state."""
        self._root.deiconify()
        self._visible = True
        self._status_label.config(text="Analyzing screenshot...", fg=self.LOADING_COLOR)
        self._set_response_text("Analyzing your screen with Gemini AI...", color=self.LOADING_COLOR)
        self._root.lift()

    def show_response(self, response_text: str, screenshot_path: str = None) -> None:
        """Display the AI response in the overlay."""
        self._root.after(0, lambda: self._show_response_main_thread(response_text, screenshot_path))

    def _show_response_main_thread(self, response_text: str, screenshot_path: str = None) -> None:
        """Internal: called on the main thread to show the response."""
        self._root.deiconify()
        self._visible = True
        self._status_label.config(text="Analysis complete", fg=self.ACCENT_COLOR)
        self._set_response_text(response_text)
        self._root.lift()

        try:
            from api_client import query_followup
            self._on_followup_callback = query_followup
        except ImportError:
            pass

    def show_error(self, error_message: str) -> None:
        """Display an error message in the overlay."""
        self._root.after(0, lambda: self._show_error_main_thread(error_message))

    def _show_error_main_thread(self, error_message: str) -> None:
        """Internal: called on the main thread to show an error."""
        self._root.deiconify()
        self._visible = True
        self._status_label.config(text="Error occurred", fg=self.ERROR_COLOR)
        self._set_response_text(f"Error: {error_message}", color=self.ERROR_COLOR)
        self._root.lift()

    def hide(self) -> None:
        """Hide the overlay window."""
        self._root.withdraw()
        self._visible = False

    def is_visible(self) -> bool:
        """Return whether the overlay is currently visible."""
        return self._visible

    def run(self) -> None:
        """Start the tkinter event loop. Blocks until window is closed."""
        self._root.mainloop()
