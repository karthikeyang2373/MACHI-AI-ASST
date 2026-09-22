"""
MACHI - Modern AI Voice Assistant GUI
A premium dark-themed customtkinter interface for Windows laptops.
"""
import threading
import queue
import time
import datetime
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional
from config import ASSISTANT_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, VERSION, APP_TITLE
from utils.logger import logger

# Premium Cyberpunk / Modern Dark Palette
COLORS = {
    "bg_primary": "#0A0A0F",
    "bg_secondary": "#12121A",
    "bg_card": "#181824",
    "bg_card2": "#202030",
    "accent_blue": "#3B82F6",
    "accent_purple": "#8B5CF6",
    "accent_cyan": "#06B6D4",
    "accent_green": "#10B981",
    "accent_red": "#EF4444",
    "accent_orange": "#F59E0B",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_dim": "#475569",
    "glow_blue": "#1E3A5F",
    "border": "#28283C",
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ChatBubble(ctk.CTkFrame):
    """A single chat message bubble."""

    def __init__(self, parent, sender: str, message: str, timestamp: str, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        is_user = sender.lower() == "user"

        bubble_color = COLORS["glow_blue"] if is_user else COLORS["bg_card"]
        text_color = COLORS["text_primary"]
        border_color = COLORS["accent_blue"] if is_user else COLORS["border"]
        anchor = "e" if is_user else "w"

        sender_label = ctk.CTkLabel(
            self,
            text=f"  {'You' if is_user else ASSISTANT_NAME}  •  {timestamp}",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"],
            anchor=anchor
        )
        sender_label.pack(anchor=anchor, padx=12)

        bubble = ctk.CTkFrame(
            self,
            fg_color=bubble_color,
            border_color=border_color,
            border_width=1,
            corner_radius=14
        )
        bubble.pack(anchor=anchor, padx=8, pady=2, fill="x" if not is_user else None)

        msg_label = ctk.CTkLabel(
            bubble,
            text=message,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=text_color,
            wraplength=560,
            justify="left",
            anchor="w"
        )
        msg_label.pack(padx=16, pady=10)


class MachiGUI(ctk.CTk):
    """Main MACHI AI Assistant GUI Window."""

    def __init__(self):
        super().__init__()
        self._on_command_callback: Optional[Callable] = None
        self._on_manual_listen_callback: Optional[Callable] = None
        self._is_listening = False
        self._is_speaking = False
        self._message_queue = queue.Queue()

        self._setup_window()
        self._build_ui()
        self._start_message_processor()
        self._animate_status_dot()

    def _setup_window(self):
        self.title(f"{APP_TITLE} (v{VERSION})")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(960, 620)
        self.configure(fg_color=COLORS["bg_primary"])
        self.resizable(True, True)

        # Center on screen
        self.update_idletasks()
        x = max(0, (self.winfo_screenwidth() - WINDOW_WIDTH) // 2)
        y = max(0, (self.winfo_screenheight() - WINDOW_HEIGHT) // 2)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _build_ui(self):
        """Build the full UI layout."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        """Left sidebar with brand, status, quick commands, and controls."""
        sidebar = ctk.CTkFrame(
            self,
            width=260,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(20, weight=1)
        sidebar.grid_propagate(False)

        # Brand header
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=18, pady=(22, 6))

        logo_label = ctk.CTkLabel(
            brand_frame,
            text="⚡ MACHI AI",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["accent_blue"]
        )
        logo_label.pack(anchor="w")

        tagline = ctk.CTkLabel(
            brand_frame,
            text="Voice Control Laptop Assistant",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_secondary"]
        )
        tagline.pack(anchor="w")

        # Divider
        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=10)

        # Status badge
        status_frame = ctk.CTkFrame(sidebar, fg_color=COLORS["bg_card"], corner_radius=10)
        status_frame.pack(fill="x", padx=14, pady=4)

        self._status_dot = ctk.CTkLabel(
            status_frame, text="●", font=ctk.CTkFont(size=14),
            text_color=COLORS["accent_green"]
        )
        self._status_dot.pack(side="left", padx=(12, 6), pady=8)

        self._status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self._status_label.pack(side="left", pady=8)

        # Wake word card
        wake_frame = ctk.CTkFrame(sidebar, fg_color=COLORS["bg_card"], corner_radius=10)
        wake_frame.pack(fill="x", padx=14, pady=6)

        ctk.CTkLabel(
            wake_frame,
            text="WAKE WORD",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLORS["text_dim"]
        ).pack(anchor="w", padx=12, pady=(8, 0))

        ctk.CTkLabel(
            wake_frame,
            text='"Hey MACHI"',
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["accent_cyan"]
        ).pack(anchor="w", padx=12, pady=(2, 8))

        # Quick Commands
        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(
            sidebar,
            text="QUICK ACTIONS",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLORS["text_dim"]
        ).pack(anchor="w", padx=16, pady=(4, 6))

        quick_cmds = [
            ("🔊 Volume Up", "increase volume"),
            ("🔇 Mute Audio", "mute"),
            ("📸 Take Screenshot", "take screenshot"),
            ("💻 System Info", "show system info"),
            ("🌐 Open Chrome", "open chrome"),
            ("⏯️ Play / Pause", "play music"),
        ]
        for label, cmd in quick_cmds:
            btn = ctk.CTkButton(
                sidebar,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                fg_color=COLORS["bg_card2"],
                hover_color=COLORS["glow_blue"],
                text_color=COLORS["text_primary"],
                border_color=COLORS["border"],
                border_width=1,
                corner_radius=8,
                height=32,
                anchor="w",
                command=lambda c=cmd: self._send_quick_command(c)
            )
            btn.pack(fill="x", padx=14, pady=2)

        # Bottom Actions: Mute & Clear
        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=8)

        self._mute_var = ctk.BooleanVar(value=False)
        self._mute_btn = ctk.CTkButton(
            sidebar,
            text="🎙️ Mic: Listening",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=COLORS["accent_green"],
            hover_color="#059669",
            text_color="white",
            corner_radius=8,
            height=36,
            command=self._toggle_mic
        )
        self._mute_btn.pack(fill="x", padx=14, pady=3)

        ctk.CTkButton(
            sidebar,
            text="🗑️ Clear History",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=COLORS["bg_card2"],
            hover_color="#3A1D28",
            text_color=COLORS["text_secondary"],
            corner_radius=8,
            height=30,
            command=self._clear_chat
        ).pack(fill="x", padx=14, pady=3)

    def _build_main_area(self):
        """Right main content area with header, chat view, and command bar."""
        main = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Header bar
        header = ctk.CTkFrame(
            main, height=54, fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"], border_width=1, corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="💬 Voice & Command Console",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=12)

        self._time_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]
        )
        self._time_label.pack(side="right", padx=20)
        self._update_time()

        # Chat scrollable area
        self._chat_scroll = ctk.CTkScrollableFrame(
            main,
            fg_color=COLORS["bg_primary"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent_blue"]
        )
        self._chat_scroll.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self._chat_scroll.grid_columnconfigure(0, weight=1)

        # Bottom Input Area
        input_frame = ctk.CTkFrame(
            main,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"],
            border_width=1,
            height=76,
            corner_radius=0
        )
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.pack_propagate(False)

        self._text_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Say 'Hey MACHI' or type any command (e.g. 'open notepad', 'volume 50%', 'check cpu')...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_dim"],
            corner_radius=10,
            height=44
        )
        self._text_input.pack(side="left", fill="x", expand=True, padx=(18, 8), pady=16)
        self._text_input.bind("<Return>", self._on_enter_key)

        # Send button
        self._send_btn = ctk.CTkButton(
            input_frame,
            text="➤",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["accent_blue"],
            hover_color="#2563EB",
            width=48,
            height=44,
            corner_radius=10,
            command=self._on_send
        )
        self._send_btn.pack(side="left", padx=(0, 6), pady=16)

        # Mic button
        self._voice_btn = ctk.CTkButton(
            input_frame,
            text="🎙️",
            font=ctk.CTkFont(size=18),
            fg_color=COLORS["accent_purple"],
            hover_color="#7C3AED",
            width=48,
            height=44,
            corner_radius=10,
            command=self._on_manual_listen
        )
        self._voice_btn.pack(side="left", padx=(0, 18), pady=16)

        # Initial welcome message
        self.add_message("MACHI", f"Hello! I am {ASSISTANT_NAME}, your AI Voice Control Laptop Assistant. Say **Hey MACHI** or speak/type any command to get started!", speak=False)

    # ---- Public Interface ----

    def set_command_callback(self, callback: Callable):
        self._on_command_callback = callback

    def set_manual_listen_callback(self, callback: Callable):
        self._on_manual_listen_callback = callback

    def add_message(self, sender: str, message: str, speak: bool = True):
        self._message_queue.put(("message", sender, message))

    def set_status(self, status: str, color: str = None):
        self._message_queue.put(("status", status, color or COLORS["accent_green"]))

    def set_listening(self, listening: bool):
        self._message_queue.put(("listening", listening, None))

    def show_confirmation_dialog(self, description: str, on_confirm: Callable, on_cancel: Callable):
        self._message_queue.put(("confirm", description, (on_confirm, on_cancel)))

    # ---- Internal Event Loops ----

    def _start_message_processor(self):
        def process():
            try:
                while not self._message_queue.empty():
                    item = self._message_queue.get_nowait()
                    msg_type = item[0]
                    if msg_type == "message":
                        _, sender, msg = item
                        self._add_bubble(sender, msg)
                    elif msg_type == "status":
                        _, status, color = item
                        self._status_label.configure(text=status)
                        self._status_dot.configure(text_color=color)
                    elif msg_type == "listening":
                        _, is_listening, _ = item
                        self._is_listening = is_listening
                        if is_listening:
                            self.set_status("Listening...", COLORS["accent_cyan"])
                        else:
                            self.set_status("Ready", COLORS["accent_green"])
                    elif msg_type == "confirm":
                        _, desc, callbacks = item
                        self._show_confirm_dialog(desc, callbacks[0], callbacks[1])
            except queue.Empty:
                pass
            self.after(50, process)

        self.after(50, process)

    def _add_bubble(self, sender: str, message: str):
        ts = datetime.datetime.now().strftime("%H:%M")
        bubble = ChatBubble(
            self._chat_scroll,
            sender=sender,
            message=message,
            timestamp=ts
        )
        bubble.pack(fill="x", padx=8, pady=4)
        self.after(100, lambda: self._chat_scroll._parent_canvas.yview_moveto(1.0))

    def _on_enter_key(self, event):
        self._on_send()

    def _on_send(self):
        text = self._text_input.get().strip()
        if not text:
            return
        self._text_input.delete(0, "end")
        self.add_message("User", text)
        if self._on_command_callback:
            threading.Thread(target=self._on_command_callback, args=(text,), daemon=True).start()

    def _on_manual_listen(self):
        if self._on_manual_listen_callback:
            threading.Thread(target=self._on_manual_listen_callback, daemon=True).start()

    def _send_quick_command(self, cmd: str):
        self.add_message("User", cmd)
        if self._on_command_callback:
            threading.Thread(target=self._on_command_callback, args=(cmd,), daemon=True).start()

    def _toggle_mic(self):
        self._mute_var.set(not self._mute_var.get())
        if self._mute_var.get():
            self._mute_btn.configure(text="🔇 Mic: Muted", fg_color=COLORS["accent_red"])
        else:
            self._mute_btn.configure(text="🎙️ Mic: Listening", fg_color=COLORS["accent_green"])

    def is_mic_muted(self) -> bool:
        return self._mute_var.get()

    def _clear_chat(self):
        for widget in self._chat_scroll.winfo_children():
            widget.destroy()

    def _show_confirm_dialog(self, description: str, on_confirm: Callable, on_cancel: Callable):
        result = messagebox.askyesno(
            "MACHI Security Confirmation",
            f"⚠️ Confirm Action:\n\n{description}\n\nDo you want to proceed?",
            parent=self
        )
        if result:
            on_confirm()
        else:
            on_cancel()

    def _animate_status_dot(self):
        colors = [COLORS["accent_green"], "#059669", COLORS["accent_green"], "#34D399"]
        self._dot_idx = 0

        def pulse():
            if not self._is_listening and not self._is_speaking:
                self._status_dot.configure(text_color=colors[self._dot_idx % len(colors)])
                self._dot_idx += 1
            self.after(800, pulse)

        self.after(800, pulse)

    def _update_time(self):
        now = datetime.datetime.now().strftime("%a, %b %d  •  %I:%M %p")
        self._time_label.configure(text=now)
        self.after(30000, self._update_time)
