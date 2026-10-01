# memory/memory_manager.py
from memory.bitmap import BitmapSimulator
from memory.linked_list import LinkedListSimulator
from memory.buddy import BuddySimulator
from memory.page_replacement import PageReplacementSimulator

class MemoryManager:
    def __init__(self, total_memory: int = 1024):
        # Memoria total fija definida por el programa (ej. 400 MB)
        self.total_memory = total_memory
        
        # Placeholders para los 4 simuladores independientes (Fases 3 a 10)
        self.bitmap_sim = BitmapSimulator(self.total_memory)
        self.linked_list_sim = LinkedListSimulator(self.total_memory)
        self.buddy_sim = BuddySimulator(self.total_memory)
        self.page_replacement_sim = self.page_replacement_sim = PageReplacementSimulator()

    # Dejamos métodos genéricos vacíos o de error por ahora 
    # para no romper el Kernel actual si intentamos usar el comando 'run'
    def allocate(self, pid: int, required_memory: int) -> bool:
        # Por ahora, el comando 'run' de la terminal siempre fallará 
        # hasta que conectemos los nuevos simuladores.
        return False

    def release(self, pid: int):
        pass

    def get_status(self) -> str:
        return "Admon. Memoria en reconstrucción (Fase 1/2 zzzOS)."

    def tick(self):
        """Avanza el reloj de todos los simuladores activos simultáneamente."""
        if self.bitmap_sim and self.bitmap_sim.is_configured:
            self.bitmap_sim.tick()
            
        if self.linked_list_sim:
            self.linked_list_sim.tick()
            
        if self.buddy_sim:
            self.buddy_sim.tick()