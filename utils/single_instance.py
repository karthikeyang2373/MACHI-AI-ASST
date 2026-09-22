import socket
import threading
from typing import Callable, Optional
from utils.logger import logger

DEFAULT_PORT = 49872

class SingleInstanceGuard:
    """
    Prevents multiple Machi processes from running simultaneously.
    If a process is already running, sends IPC launch flags ('gui' or 'widget')
    to the primary instance and exits.
    """

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self._on_ipc_command: Optional[Callable[[str], None]] = None

    def acquire(self, mode: str = "widget") -> bool:
        """
        Attempts to bind the local IPC port.
        If port is already bound, sends mode parameter to primary process and returns False.
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("127.0.0.1", self.port))
            self.server_socket.listen(5)
            logger.info("Acquired single-instance IPC lock.")
            return True
        except socket.error:
            # Instance is already running -> send mode to existing instance
            logger.info(f"Existing instance detected. Sending command '{mode}' to active Machi instance.")
            self._send_ipc_message(mode)
            return False

    def _send_ipc_message(self, message: str):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", self.port))
            client.sendall(message.encode("utf-8"))
            client.close()
        except Exception as e:
            logger.error(f"Error sending IPC message: {e}")

    def start_listener(self, callback: Callable[[str], None]):
        """Starts background IPC server listening for incoming commands from secondary processes."""
        self._on_ipc_command = callback

        def listen_loop():
            while self.server_socket:
                try:
                    conn, _ = self.server_socket.accept()
                    data = conn.recv(1024).decode("utf-8").strip()
                    conn.close()
                    if data and self._on_ipc_command:
                        logger.info(f"IPC command received: '{data}'")
                        self._on_ipc_command(data)
                except Exception:
                    break

        threading.Thread(target=listen_loop, daemon=True).start()

    def release(self):
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None


single_instance_guard = SingleInstanceGuard()
