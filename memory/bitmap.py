# memory/bitmap.py
import math

class BitmapSimulator:
    def __init__(self, total_memory: int):
        self.total_memory = total_memory
        self.allocation_unit = 0
        self.total_cells = 0
        self.cells = []       # Representación lógica de la cuadrícula
        self.processes = {}   # Diccionario PID -> Datos del proceso
        self.is_configured = False

    def configure(self, allocation_unit: int):
        """Configura la unidad de asignación antes de iniciar la simulación."""
        if allocation_unit <= 0 or allocation_unit > self.total_memory:
            return False
            
        self.allocation_unit = allocation_unit
        self.total_cells = self.total_memory // allocation_unit
        
        # Cada celda guarda su estado (0=Libre, 1=Ocupado) y su detalle de fragmentación
        self.cells = [{
            "state": 0, 
            "pid": None, 
            "used_mb": 0, 
            "frag_mb": 0
        } for _ in range(self.total_cells)]
        
        self.processes.clear()
        self.is_configured = True
        return True

    def allocate(self, pid: int, name: str, required_memory: int, time: int) -> bool:
        """Asigna memoria buscando celdas contiguas disponibles."""
        if not self.is_configured or required_memory <= 0:
            return False
            
        cells_needed = math.ceil(required_memory / self.allocation_unit)
        
        # 1. Buscar celdas contiguas (Primer Ajuste / First Fit implícito para arrays)
        start_index = -1
        free_count = 0
        
        for i, cell in enumerate(self.cells):
            if cell["state"] == 0:
                if free_count == 0:
                    start_index = i
                free_count += 1
                if free_count == cells_needed:
                    break
            else:
                free_count = 0  # Reiniciar contador si encontramos una celda ocupada
                start_index = -1

        # 2. Si encontramos espacio, asignamos
        if free_count == cells_needed:
            allocated_indices = []
            remaining_mem = required_memory
            
            for i in range(start_index, start_index + cells_needed):
                self.cells[i]["state"] = 1
                self.cells[i]["pid"] = pid
                
                # Cálculo de la fragmentación interna por celda
                if remaining_mem >= self.allocation_unit:
                    self.cells[i]["used_mb"] = self.allocation_unit
                    self.cells[i]["frag_mb"] = 0
                    remaining_mem -= self.allocation_unit
                else:
                    self.cells[i]["used_mb"] = remaining_mem
                    self.cells[i]["frag_mb"] = self.allocation_unit - remaining_mem
                    remaining_mem = 0
                    
                allocated_indices.append(i)
                
            # Registrar el proceso
            self.processes[pid] = {
                "name": name,
                "required_memory": required_memory,
                "time": time,
                "remaining_time": time,
                "cells": allocated_indices
            }
            return True
            
        return False # No hay espacio contiguo suficiente

    def release(self, pid: int):
        """Libera las celdas ocupadas por un proceso."""
        if pid in self.processes:
            for i in self.processes[pid]["cells"]:
                self.cells[i] = {
                    "state": 0, 
                    "pid": None, 
                    "used_mb": 0, 
                    "frag_mb": 0
                }
            del self.processes[pid]
            return True
        return False
        
    def tick(self):
        """Disminuye el tiempo de los procesos y libera los que llegan a 0."""
        completed_pids = []
        for pid, p_data in self.processes.items():
            p_data["remaining_time"] -= 1
            if p_data["remaining_time"] <= 0:
                completed_pids.append(pid)
                
        for pid in completed_pids:
            self.release(pid)