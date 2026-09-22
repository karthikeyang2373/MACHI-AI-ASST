import psutil
import platform
import socket
import datetime
from typing import Tuple
from utils.logger import logger


class SystemMonitor:
    """Provides system information including CPU, RAM, battery, disk, network, and time."""

    def get_cpu_usage(self) -> Tuple[bool, str]:
        cpu = psutil.cpu_percent(interval=0.5)
        msg = f"CPU usage is {cpu:.1f} percent."
        logger.info(msg)
        return True, msg

    def get_ram_usage(self) -> Tuple[bool, str]:
        ram = psutil.virtual_memory()
        used_gb = ram.used / (1024 ** 3)
        total_gb = ram.total / (1024 ** 3)
        msg = f"RAM usage is {ram.percent:.1f} percent. {used_gb:.1f} GB of {total_gb:.1f} GB is currently in use."
        logger.info(msg)
        return True, msg

    def get_battery_status(self) -> Tuple[bool, str]:
        battery = psutil.sensors_battery()
        if battery is None:
            return False, "No battery detected. Running on AC desktop power."
        status = "charging" if battery.power_plugged else "discharging"
        msg = f"Battery is at {battery.percent:.0f} percent and is currently {status}."
        if not battery.power_plugged and battery.percent < 20:
            msg += " Please connect your laptop charger."
        logger.info(msg)
        return True, msg

    def get_disk_usage(self) -> Tuple[bool, str]:
        disk = psutil.disk_usage("C:\\")
        used_gb = disk.used / (1024 ** 3)
        total_gb = disk.total / (1024 ** 3)
        free_gb = disk.free / (1024 ** 3)
        msg = f"Local disk C is {disk.percent:.1f} percent full with {free_gb:.1f} GB free out of {total_gb:.1f} GB."
        logger.info(msg)
        return True, msg

    def get_network_info(self) -> Tuple[bool, str]:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            msg = f"Connected on network. Device: {hostname}, Local IP address: {local_ip}."
            return True, msg
        except Exception as e:
            return False, f"Could not retrieve network status: {e}"

    def get_time(self) -> Tuple[bool, str]:
        now = datetime.datetime.now()
        return True, f"The current time is {now.strftime('%I:%M %p')}."

    def get_date(self) -> Tuple[bool, str]:
        now = datetime.datetime.now()
        return True, f"Today is {now.strftime('%A, %B %d, %Y')}."

    def get_all_info(self) -> Tuple[bool, str]:
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")
        battery = psutil.sensors_battery()

        parts = [
            f"CPU: {cpu:.0f}%",
            f"RAM: {ram.percent:.0f}%",
            f"Disk C: {disk.percent:.0f}% used",
        ]
        if battery:
            parts.append(f"Battery: {battery.percent:.0f}% ({'charging' if battery.power_plugged else 'unplugged'})")

        msg = "System summary: " + " | ".join(parts) + "."
        logger.info(msg)
        return True, msg

    def get_info(self, info_type: str) -> Tuple[bool, str]:
        t = info_type.lower()
        if t == "cpu":
            return self.get_cpu_usage()
        elif t in ["ram", "memory"]:
            return self.get_ram_usage()
        elif t in ["battery", "batt"]:
            return self.get_battery_status()
        elif t in ["disk", "storage"]:
            return self.get_disk_usage()
        elif t in ["network", "ip", "wifi"]:
            return self.get_network_info()
        elif t == "time":
            return self.get_time()
        elif t == "date":
            return self.get_date()
        else:
            return self.get_all_info()


system_monitor = SystemMonitor()
