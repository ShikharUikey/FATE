import psutil
from typing import Dict, Any, List

class DesktopSystemMonitor:
    """Monitors system resource usage (CPU, RAM, Disk, active processes)."""

    def get_system_telemetry(self) -> Dict[str, Any]:
        """Collects host resource metrics in real-time."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "battery_percent": psutil.sensors_battery().percent if psutil.sensors_battery() else 100.0,
            "uptime_seconds": int(psutil.boot_time())
        }

    def list_active_processes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists active running process metrics on the host."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu_usage": info['cpu_percent'],
                    "ram_usage": info['memory_percent']
                })
                if len(processes) >= limit:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    def kill_process_by_pid(self, pid: int) -> bool:
        """Kills a target system process."""
        try:
            p = psutil.Process(pid)
            p.terminate()
            return True
        except Exception:
            return False
