"""
MACHI - Floating Mini Voice Widget
A sleek, minimal, top-right floating microphone widget for Windows.
"""
import sys
import tkinter as tk
import customtkinter as ctk
import threading
import queue
from typing import Callable, Optional
from config import ASSISTANT_NAME, VERSION

# Premium Dark Widget Color Palette
WIDGET_COLORS = {
    "bg": "#12121A",
    "card": "#1A1A26",
    "border": "#3B82F6",
    "border_listening": "#06B6D4",
    "accent_blue": "#3B82F6",
    "accent_cyan": "#06B6D4",
    "accent_purple": "#8B5CF6",
    "accent_red": "#EF4444",
    "accent_green": "#10B981",
    "text_primary": "#F8FAFC",
    "text_dim": "#94A3B8"
}


class MachiMiniWidget(ctk.CTk):
    """Floating top-right mini microphone widget for MACHI."""

    def __init__(self, on_open_gui: Optional[Callable] = None, on_exit: Optional[Callable] = None):
        super().__init__()
        self.on_open_gui = on_open_gui
        self.on_exit = on_exit
        self._on_listen_callback: Optional[Callable] = None
        self._is_listening = False
        self._message_queue = queue.Queue()

        # Frameless stay-on-top window setup
        self._setup_window()
        self._build_ui()
        self._bind_mouse_drag()
        self._start_message_processor()

    def _setup_window(self):
        self.title("MACHI Mini")
        self.overrideredirect(True)  # Remove standard window frame
        self.attributes("-topmost", True)  # Always stay on top
        self.configure(fg_color=WIDGET_COLORS["bg"])

        # Top-right corner positioning
        self.update_idletasks()
        width, height = 200, 72
        screen_w = self.winfo_screenwidth()
        x = max(10, screen_w - width - 24)
        y = 36
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        """Constructs the sleek floating card."""
        self._card = ctk.CTkFrame(
            self,
            fg_color=WIDGET_COLORS["card"],
            border_color=WIDGET_COLORS["border"],
            border_width=2,
            corner_radius=16
        )
        self._card.pack(fill="both", expand=True, padx=2, pady=2)

        # Left side: Interactive Mic Button
        self._mic_btn = ctk.CTkButton(
            self._card,
            text="🎤",
            font=ctk.CTkFont(size=22),
            fg_color=WIDGET_COLORS["accent_purple"],
            hover_color="#7C3AED",
            width=46,
            height=46,
            corner_radius=12,
            command=self._on_mic_click
        )
        self._mic_btn.pack(side="left", padx=(10, 8), pady=10)

        # Center area: Brand & Status Labels
        info_frame = ctk.CTkFrame(self._card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=10)

        title_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_row.pack(anchor="w")

        title_label = ctk.CTkLabel(
            title_row,
            text="MACHI",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=WIDGET_COLORS["accent_cyan"]
        )
        title_label.pack(side="left")

        # Right-click menu trigger button on title
        gui_btn = ctk.CTkButton(
            title_row,
            text="↗",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="transparent",
            hover_color="#2A2A3D",
            text_color=WIDGET_COLORS["text_dim"],
            width=20,
            height=18,
            corner_radius=4,
            command=self._open_gui_trigger
        )
        gui_btn.pack(side="left", padx=(4, 0))

        self._status_label = ctk.CTkLabel(
            info_frame,
            text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=WIDGET_COLORS["accent_green"],
            anchor="w"
        )
        self._status_label.pack(anchor="w")

        # Right-click context menu bindings
        self._card.bind("<Button-3>", self._show_context_menu)
        self.bind("<Button-3>", self._show_context_menu)

    def set_listen_callback(self, callback: Callable):
        self._on_listen_callback = callback

    def is_mic_muted(self) -> bool:
        """Returns True if the microphone is muted."""
        return getattr(self, "_is_muted", False)

    def set_status(self, text: str, color: str = None):
        self._message_queue.put(("status", text, color or WIDGET_COLORS["accent_green"]))

    def set_listening(self, listening: bool):
        self._message_queue.put(("listening", listening, None))

    def _start_message_processor(self):
        def process():
            try:
                while not self._message_queue.empty():
                    item = self._message_queue.get_nowait()
                    mtype = item[0]
                    if mtype == "status":
                        _, text, color = item
                        self._status_label.configure(text=text, text_color=color)
                    elif mtype == "listening":
                        _, listening, _ = item
                        self._is_listening = listening
                        if listening:
                            self._status_label.configure(text="🔴 Listening...", text_color=WIDGET_COLORS["accent_cyan"])
                            self._card.configure(border_color=WIDGET_COLORS["accent_cyan"])
                            self._mic_btn.configure(fg_color=WIDGET_COLORS["accent_red"])
                        else:
                            self._status_label.configure(text="Ready", text_color=WIDGET_COLORS["accent_green"])
                            self._card.configure(border_color=WIDGET_COLORS["border"])
                            self._mic_btn.configure(fg_color=WIDGET_COLORS["accent_purple"])
            except queue.Empty:
                pass
            self.after(50, process)

        self.after(50, process)

    def _on_mic_click(self):
        if self._on_listen_callback:
            threading.Thread(target=self._on_listen_callback, daemon=True).start()

    def _open_gui_trigger(self):
        if self.on_open_gui:
            self.on_open_gui()

    def _bind_mouse_drag(self):
        """Allows user to click and drag the widget anywhere on screen."""
        self._drag_data = {"x": 0, "y": 0}

        def on_drag_start(event):
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

        def on_drag_motion(event):
            deltax = event.x - self._drag_data["x"]
            deltay = event.y - self._drag_data["y"]
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")

        for widget in [self, self._card]:
            widget.bind("<ButtonPress-1>", on_drag_start)
            widget.bind("<B1-Motion>", on_drag_motion)

    def _show_context_menu(self, event):
        """Displays right-click context menu."""
        menu = tk.Menu(self, tearoff=0, bg="#1E1E2C", fg="#F8FAFC", activebackground="#3B82F6", activeforeground="#FFFFFF")
        menu.add_command(label="🖥️ Open Full Machi GUI", command=self._open_gui_trigger)
        menu.add_command(label="🎙️ Start Listening", command=self._on_mic_click)
        menu.add_separator()
        menu.add_command(label="❌ Exit Machi", command=self._on_exit_trigger)
        menu.tk_popup(event.x_root, event.y_root)

    def _on_exit_trigger(self):
        if self.on_exit:
            self.on_exit()
        else:
            self.destroy()
            sys.exit(0)
