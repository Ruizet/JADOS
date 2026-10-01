# process/scheduling/round_robin.py
from process.scheduling.scheduler import Scheduler

class RoundRobinScheduler(Scheduler):
    def __init__(self, quantum: int):
        super().__init__()
        self.quantum = quantum
        self.current_quantum_time = 0
        self.active_queue = [] # Procesos que ya llegaron y están dando vueltas
        self.unstarted_processes = [] # Procesos creados pero que aún no es su tiempo de llegada

    def add_process(self, process):
        process.state = "NEW"
        self.unstarted_processes.append(process)

    def tick(self, current_time: int):
        # 1. Admitir procesos nuevos cuyo tiempo de llegada ya se cumplió
        arrived_now = [p for p in self.unstarted_processes if p.arrival_time <= current_time]
        arrived_now.sort(key=lambda p: (p.arrival_time, p.pid))
        for p in arrived_now:
            p.state = "READY"
            self.active_queue.append(p)
            self.unstarted_processes.remove(p)

        terminated_pid = None

        # 2. Ejecutar el proceso actual
        if self.current_process:
            self.current_process.remaining_time -= 1
            self.current_quantum_time += 1

            # Si terminó antes o justo al límite del quantum
            if self.current_process.remaining_time <= 0:
                self.current_process.state = "TERMINATED"
                self._calculate_metrics(self.current_process, current_time + 1)
                self.completed_processes.append(self.current_process)
                terminated_pid = self.current_process.pid
                self.current_process = None
                self.current_quantum_time = 0
                
            # Si se le acabó el quantum pero no ha terminado (Interrupción / Context Switch)
            elif self.current_quantum_time >= self.quantum:
                self.current_process.state = "READY"
                self.active_queue.append(self.current_process) # Vuelve al final de la cola
                self.current_process = None
                self.current_quantum_time = 0

        # 3. Asignar la CPU al siguiente de la cola si está libre
        if self.current_process is None and self.active_queue:
            self.current_process = self.active_queue.pop(0) # Saca el primero
            self.current_process.state = "RUNNING"
            if self.current_process.start_time == -1:
                self.current_process.start_time = current_time
                self.current_process.response_time = current_time - self.current_process.arrival_time

        return terminated_pid