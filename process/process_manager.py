# process/process_manager.py
from process.process import Process

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.scheduler = None
        self.next_pid = 1
        
    def set_scheduler(self, scheduler_instance):
        self.scheduler = scheduler_instance

    def create_process(self, name: str, arrival_time: int, burst_time: int, priority: int = 0, queue_level: int = 0, guaranteed_pct: float = 0.0) -> int:
        pid = self.next_pid
        p = Process(pid, name, arrival_time, burst_time, priority, queue_level, guaranteed_pct)
        self.processes[pid] = p
        self.next_pid += 1
        
        if self.scheduler:
            self.scheduler.add_process(p)
            
        return pid

    def execute_cycle(self, current_time: int) -> int:
        """Delega la ejecución del ciclo al algoritmo de planificación seleccionado. Retorna PID si uno termina."""
        if self.scheduler:
            return self.scheduler.tick(current_time)
        return None

    def get_all_processes(self):
        """Devuelve una lista con todos los objetos de proceso instanciados."""
        return list(self.processes.values())