# process/scheduling/guaranteed.py
from process.scheduling.scheduler import Scheduler

class GuaranteedScheduler(Scheduler):
    def __init__(self):
        super().__init__()
        self.unstarted = []

    def add_process(self, process):
        process.state = "NEW"
        # Propiedad dinámica para rastrear cuánto CPU ha consumido realmente
        process.cpu_received = 0 
        self.unstarted.append(process)

    def tick(self, current_time: int):
        for p in [p for p in self.unstarted if p.arrival_time <= current_time]:
            p.state = "READY"
            self.ready_queue.append(p)
            self.unstarted.remove(p)

        terminated_pid = None

        if self.current_process:
            self.current_process.remaining_time -= 1
            self.current_process.cpu_received += 1
            
            if self.current_process.state == "TERMINATED" or self.current_process.remaining_time <= 0:
                self.current_process.state = "TERMINATED"
                self._calculate_metrics(self.current_process, current_time + 1)
                self.completed_processes.append(self.current_process)
                terminated_pid = self.current_process.pid
                self.current_process = None
            else:
                # Regresamos el proceso a la cola para reevaluar a quién le toca (Preemptive)
                self.current_process.state = "READY"
                self.ready_queue.append(self.current_process)
                self.current_process = None

        # Evaluación matemática: Seleccionamos al que esté "más atrasado" respecto a su cuota
        if self.ready_queue:
            best_ratio = float('inf')
            best_process = None
            
            for p in self.ready_queue:
                time_in_system = max(1, current_time - p.arrival_time)
                entitled_cpu = time_in_system * (max(1.0, p.guaranteed_pct) / 100.0)
                ratio = p.cpu_received / entitled_cpu
                
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_process = p

            self.current_process = best_process
            self.ready_queue.remove(self.current_process)
            self.current_process.state = "RUNNING"
            if self.current_process.start_time == -1:
                self.current_process.start_time = current_time
                self.current_process.response_time = current_time - self.current_process.arrival_time

        return terminated_pid