# memory/memory_manager.py
from memory.partition import PartitionManager

class MemoryManager:
    def __init__(self, total_ram: int = 1024):
        self.total_ram = total_ram
        self.backend = PartitionManager()

    def allocate(self, pid: int, required_memory: int) -> bool:
        return self.backend.allocate(pid, required_memory)

    def release(self, pid: int):
        self.backend.release(pid)

    def get_status(self) -> str:
        return self.backend.get_status()

    def get_raw_data(self) -> list:
        """Pide los datos estructurados al backend activo (Particiones o Paginación)."""
        return self.backend.get_raw_data()