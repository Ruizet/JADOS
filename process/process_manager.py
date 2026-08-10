# process/process_manager.py
from process.process import Process, ProcessState

class ProcessManager:
    def __init__(self):
        self.processes = {}  
        self.next_pid = 1
        
        # --- Variables del Scheduler ---
        self.ready_queue = []        # Cola de procesos esperando CPU
        self.running_process = None  # Proceso actualmente en la CPU

    def create_process(self, name: str, memory: int, time: int, priority: int = 0) -> Process:
        process = Process(self.next_pid, name, memory, time, priority)
        self.processes[self.next_pid] = process
        self.next_pid += 1
        
        # En esta fase, pasamos directamente a READY. 
        # (En la Fase 5, validaremos si hay RAM antes de hacer esto)
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        
        return process

    def get_all_processes(self) -> list:
        return list(self.processes.values())
        
    def get_process_by_pid(self, pid: int) -> Process:
        return self.processes.get(pid)

    def execute_cycle(self) -> int:
        """Simula un tick de CPU. Retorna el PID si un proceso termina, de lo contrario None."""
        terminated_pid = None
        
        # 1. Avanzar tiempo del proceso actual
        if self.running_process:
            self.running_process.remaining_time -= 1
            
            if self.running_process.remaining_time <= 0:
                self.running_process.state = ProcessState.TERMINATED
                terminated_pid = self.running_process.pid
                self.running_process = None

        # 2. Planificador (Scheduler)
        if not self.running_process and self.ready_queue:
            self.running_process = self.ready_queue.pop(0)
            self.running_process.state = ProcessState.RUNNING
            
        return terminated_pid

    def kill_process(self, pid: int) -> bool:
        """Finaliza un proceso de manera forzada."""
        process = self.get_process_by_pid(pid)
        if not process or process.state == ProcessState.TERMINATED:
            return False
        
        process.state = ProcessState.TERMINATED
        
        if process in self.ready_queue:
            self.ready_queue.remove(process)
            
        if self.running_process and self.running_process.pid == pid:
            self.running_process = None
            
        return True