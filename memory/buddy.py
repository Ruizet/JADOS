# memory/buddy.py

class BuddyBlock:
    def __init__(self, start: int, size: int, is_free: bool = True, pid: int = None, req_mem: int = 0):
        self.start = start  # Dirección de inicio del bloque
        self.size = size    # Tamaño real asignado (Siempre potencia de 2)
        self.is_free = is_free
        self.pid = pid
        self.req_mem = req_mem # Memoria que el proceso realmente pidió

class BuddySimulator:
    def __init__(self, total_memory: int):
        self.total_memory = total_memory
        # Iniciamos con un solo bloque gigante
        self.blocks = [BuddyBlock(0, self.total_memory)]
        self.processes = {}

    def _next_power_of_2(self, x: int) -> int:
        """Devuelve la potencia de 2 más cercana hacia arriba."""
        return 1 if x == 0 else 2**(x - 1).bit_length()

    def allocate(self, pid: int, name: str, req_mem: int, time: int) -> bool:
        if req_mem <= 0 or req_mem > self.total_memory:
            return False

        target_size = max(1, self._next_power_of_2(req_mem))
        
        # 1. Buscar el bloque libre más pequeño que sea >= target_size
        best_idx = -1
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= target_size:
                if best_idx == -1 or block.size < self.blocks[best_idx].size:
                    best_idx = i
                    
        if best_idx == -1:
            return False # No hay espacio

        # 2. Dividir el bloque en mitades hasta llegar al tamaño deseado
        while self.blocks[best_idx].size > target_size:
            block = self.blocks[best_idx]
            half = block.size // 2
            
            left_buddy = BuddyBlock(block.start, half)
            right_buddy = BuddyBlock(block.start + half, half)
            
            # Reemplazar el bloque grande por sus dos mitades
            self.blocks.pop(best_idx)
            self.blocks.insert(best_idx, right_buddy)
            self.blocks.insert(best_idx, left_buddy)
            # best_idx sigue apuntando a left_buddy, que es el que seguiremos dividiendo si es necesario

        # 3. Asignar el proceso al bloque final
        self.blocks[best_idx].is_free = False
        self.blocks[best_idx].pid = pid
        self.blocks[best_idx].req_mem = req_mem
        
        self.processes[pid] = {
            "name": name,
            "req_mem": req_mem,
            "alloc_mem": target_size,
            "frag": target_size - req_mem,
            "time": time,
            "remaining_time": time
        }
        return True

    def release(self, pid: int):
        if pid not in self.processes: return False
        
        for block in self.blocks:
            if block.pid == pid:
                block.is_free = True
                block.pid = None
                block.req_mem = 0
                break
                
        del self.processes[pid]
        self._merge_buddies()
        return True

    def _merge_buddies(self):
        """Fusión iterativa de Buddies (Asociados)."""
        merged_in_pass = True
        while merged_in_pass:
            merged_in_pass = False
            i = 0
            while i < len(self.blocks) - 1:
                b1 = self.blocks[i]
                b2 = self.blocks[i+1]
                
                # Si dos bloques seguidos están libres y son del mismo tamaño...
                if b1.is_free and b2.is_free and b1.size == b2.size:
                    # Usamos la matemática de direcciones (XOR) para comprobar si son Buddies reales
                    if b1.start ^ b1.size == b2.start:
                        # ¡Se fusionan!
                        new_block = BuddyBlock(b1.start, b1.size * 2)
                        self.blocks.pop(i) # Borramos b1
                        self.blocks.pop(i) # Borramos b2 (ahora en la posición i)
                        self.blocks.insert(i, new_block)
                        merged_in_pass = True
                        continue # Re-evaluamos desde este mismo índice por si se puede seguir fusionando
                i += 1

    def tick(self):
        completed_pids = [pid for pid, p in self.processes.items() if p["remaining_time"] - 1 <= 0]
        for pid, p in self.processes.items(): p["remaining_time"] -= 1
        for pid in completed_pids: self.release(pid)