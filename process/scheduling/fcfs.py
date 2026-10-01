# process/scheduling/fcfs.py
from process.scheduling.scheduler import Scheduler

class FCFSScheduler(Scheduler):
    def __init__(self):
        super().__init__()

    def tick(self, current_time: int):
        # 1. Asegurar el orden de llegada
        self.ready_queue.sort(key=lambda p: (p.arrival_time, p.pid))
        
        # 2. Si no hay proceso actual, tomar el primero de la cola
        if self.current_process is None and self.ready_queue:
            # Solo consideramos procesos que ya hayan llegado
            available = [p for p in self.ready_queue if p.arrival_time <= current_time]
            if available:
                self.current_process = available[0]
                self.ready_queue.remove(self.current_process)
                self.current_process.state = "RUNNING"
                if self.current_process.start_time == -1:
                    self.current_process.start_time = current_time
                    self.current_process.response_time = current_time - self.current_process.arrival_time

        # 3. Ejecutar el proceso actual
        if self.current_process:
            self.current_process.remaining_time -= 1
            
            # 4. Verificar si terminó
            if self.current_process.remaining_time <= 0:
                self.current_process.state = "TERMINATED"
                self._calculate_metrics(self.current_process, current_time + 1)
                self.completed_processes.append(self.current_process)
                terminated_pid = self.current_process.pid
                self.current_process = None
                return terminated_pid
                
        return None