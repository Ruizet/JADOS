# process/process.py
from enum import Enum

class ProcessState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"

class Process:
    def __init__(self, pid: int, name: str, memory_required: int, total_time: int, priority: int = 0):
        self.pid = pid
        self.name = name
        self.state = ProcessState.NEW
        self.priority = priority
        self.memory_required = memory_required
        self.total_time = total_time
        self.remaining_time = total_time

    def to_dict(self):
        """Devuelve un diccionario con los datos del proceso para facilitar su uso en la GUI."""
        return {
            "pid": self.pid,
            "name": self.name,
            "state": self.state.value,
            "priority": self.priority,
            "memory": self.memory_required,
            "time": self.total_time
        }