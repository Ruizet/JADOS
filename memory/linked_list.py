# memory/linked_list.py

class MemoryBlock:
    def __init__(self, start: int, size: int, is_free: bool = True, pid: int = None):
        self.start = start
        self.size = size
        self.is_free = is_free
        self.pid = pid

class LinkedListSimulator:
    def __init__(self, total_memory: int):
        self.total_memory = total_memory
        # Inicia con un solo gran bloque libre del tamaño total de la memoria
        self.blocks = [MemoryBlock(0, total_memory)]
        self.processes = {}
        self.last_allocated_index = 0  # Puntero para el Next Fit

    def allocate(self, pid: int, name: str, required_memory: int, time: int, fit_type: str) -> bool:
        if required_memory <= 0 or required_memory > self.total_memory:
            return False

        target_index = -1
        
        # 1. BUSCAR EL BLOQUE SEGÚN EL ALGORITMO (Fit)
        if fit_type == "First Fit":
            for i, block in enumerate(self.blocks):
                if block.is_free and block.size >= required_memory:
                    target_index = i
                    break

        elif fit_type == "Next Fit":
            # Busca desde el último asignado hasta el final
            for i in range(self.last_allocated_index, len(self.blocks)):
                if self.blocks[i].is_free and self.blocks[i].size >= required_memory:
                    target_index = i
                    break
            # Si no encontró, busca desde el inicio hasta el último asignado
            if target_index == -1:
                for i in range(0, self.last_allocated_index):
                    if self.blocks[i].is_free and self.blocks[i].size >= required_memory:
                        target_index = i
                        break

        elif fit_type == "Best Fit":
            best_diff = float('inf')
            for i, block in enumerate(self.blocks):
                if block.is_free and block.size >= required_memory:
                    diff = block.size - required_memory
                    if diff < best_diff:
                        best_diff = diff
                        target_index = i

        elif fit_type == "Worst Fit":
            worst_diff = -1
            for i, block in enumerate(self.blocks):
                if block.is_free and block.size >= required_memory:
                    diff = block.size - required_memory
                    if diff > worst_diff:
                        worst_diff = diff
                        target_index = i

        # 2. ASIGNAR EL BLOQUE (Si se encontró uno)
        if target_index != -1:
            block = self.blocks[target_index]
            
            # Si el bloque es más grande de lo necesario, lo dividimos
            if block.size > required_memory:
                new_free_block = MemoryBlock(
                    start=block.start + required_memory,
                    size=block.size - required_memory
                )
                self.blocks.insert(target_index + 1, new_free_block)
                
            block.size = required_memory
            block.is_free = False
            block.pid = pid
            
            self.last_allocated_index = target_index

            self.processes[pid] = {
                "name": name,
                "required_memory": required_memory,
                "time": time,
                "remaining_time": time,
                "fit_type": fit_type
            }
            return True
            
        return False # Falló la asignación (Fragmentación externa)

    def release(self, pid: int):
        if pid not in self.processes:
            return False

        # Liberar el bloque
        for block in self.blocks:
            if block.pid == pid:
                block.is_free = True
                block.pid = None
                break

        del self.processes[pid]
        self._merge_free_blocks()
        return True

    def _merge_free_blocks(self):
        """Fusiona bloques libres adyacentes (Coalescing)."""
        i = 0
        while i < len(self.blocks) - 1:
            if self.blocks[i].is_free and self.blocks[i+1].is_free:
                # Fusionar bloque i con i+1
                self.blocks[i].size += self.blocks[i+1].size
                del self.blocks[i+1]
                # No incrementamos 'i' porque el nuevo bloque fusionado podría fusionarse con el siguiente
            else:
                i += 1

        # Ajustar last_allocated_index si quedó fuera de rango tras fusionar
        if self.last_allocated_index >= len(self.blocks):
            self.last_allocated_index = 0

    def tick(self):
        """Avanza el tiempo y libera procesos terminados."""
        completed_pids = []
        for pid, p in self.processes.items():
            p["remaining_time"] -= 1
            if p["remaining_time"] <= 0:
                completed_pids.append(pid)
                
        for pid in completed_pids:
            self.release(pid)