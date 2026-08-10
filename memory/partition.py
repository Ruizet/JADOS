# memory/partition.py

class Partition:
    def __init__(self, part_id: int, size: int):
        self.id = part_id
        self.size = size
        self.is_free = True
        self.process_pid = None
        self.fragmentation = 0  # Espacio desperdiciado (Fragmentación Interna)

class PartitionManager:
    def __init__(self):
        # Simulamos 1024 MB divididos en 5 particiones fijas de distintos tamaños
        self.partitions = [
            Partition(1, 64),
            Partition(2, 128),
            Partition(3, 256),
            Partition(4, 256),
            Partition(5, 320)
        ]

    def allocate(self, pid: int, required_memory: int) -> bool:
        """Asigna una partición usando el algoritmo Best-Fit (Mejor Ajuste)."""
        best_partition = None
        
        for p in self.partitions:
            if p.is_free and p.size >= required_memory:
                # Buscamos la partición que deje el menor espacio desperdiciado
                if best_partition is None or p.size < best_partition.size:
                    best_partition = p
                    
        if best_partition:
            best_partition.is_free = False
            best_partition.process_pid = pid
            # La fragmentación interna es el espacio que sobra dentro del bloque
            best_partition.fragmentation = best_partition.size - required_memory
            return True
            
        return False  # No se encontró ninguna partición adecuada

    def release(self, pid: int):
        """Libera la partición ocupada por el proceso."""
        for p in self.partitions:
            if p.process_pid == pid:
                p.is_free = True
                p.process_pid = None
                p.fragmentation = 0

    def get_status(self) -> str:
        """Genera un mapa visual del estado de las particiones."""
        out = "ID\tTAMAÑO\tESTADO\t\tPID\tFRAG. INTERNA\n"
        out += "-" * 60 + "\n"
        
        total_libre = 0
        total_frag = 0
        
        for p in self.partitions:
            estado = "Libre" if p.is_free else "Ocupado"
            pid_str = p.process_pid if p.process_pid else "-"
            frag = p.fragmentation if not p.is_free else 0
            
            if p.is_free: total_libre += p.size
            total_frag += frag
            
            out += f"{p.id}\t{p.size} MB\t{estado}\t\t{pid_str}\t{frag} MB\n"
            
        out += "-" * 60 + "\n"
        out += f"RAM Libre Total: {total_libre} MB | RAM Desperdiciada: {total_frag} MB"
        return out

    def get_raw_data(self) -> list:
        """Devuelve los datos estructurados de las particiones para la GUI."""
        data = []
        for p in self.partitions:
            data.append({
                "id": p.id,
                "size": p.size,
                "is_free": p.is_free,
                "pid": p.process_pid,
                "fragmentation": p.fragmentation if not p.is_free else 0
            })
        return data