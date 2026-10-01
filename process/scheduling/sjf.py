# process/scheduling/sjf.py
from process.scheduling.scheduler import Scheduler

class SJFScheduler(Scheduler):
    def __init__(self):
        super().__init__()

    def tick(self, current_time: int):
        # Variante No Apropiativa: Solo elegimos nuevo proceso si la CPU está libre
        if self.current_process is None and self.ready_queue:
            available = [p for p in self.ready_queue if p.arrival_time <= current_time]
            if available:
                # Ordenar por: Menor Ráfaga -> Menor Tiempo Llegada -> Menor PID
                available.sort(key=lambda p: (p.burst_time, p.arrival_time, p.pid))
                self.current_process = available[0]
                self.ready_queue.remove(self.current_process)
                self.current_process.state = "RUNNING"
                if self.current_process.start_time == -1:
                    self.current_process.start_time = current_time
                    self.current_process.response_time = current_time - self.current_process.arrival_time

        if self.current_process:
            self.current_process.remaining_time -= 1
            
            if self.current_process.remaining_time <= 0:
                self.current_process.state = "TERMINATED"
                self._calculate_metrics(self.current_process, current_time + 1)
                self.completed_processes.append(self.current_process)
                terminated_pid = self.current_process.pid
                self.current_process = None
                return terminated_pid
                
        return None