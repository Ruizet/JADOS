# process/scheduling/two_level.py
from process.scheduling.scheduler import Scheduler

class TwoLevelScheduler(Scheduler):
    def __init__(self, max_active: int, quantum: int):
        super().__init__()
        self.max_active = max_active
        self.quantum = quantum
        self.current_q_time = 0
        self.job_queue = [] # Nivel 1: Trabajos esperando ser admitidos en memoria
        self.active_queue = [] # Nivel 2: Procesos listos compitiendo por CPU

    def add_process(self, process):
        process.state = "NEW"
        self.job_queue.append(process)

    def tick(self, current_time: int):
        # 1. JOB SCHEDULER (Nivel 1): Admitir trabajos (FCFS) si hay espacio en el Nivel 2
        arrived_jobs = [p for p in self.job_queue if p.arrival_time <= current_time]
        arrived_jobs.sort(key=lambda p: (p.arrival_time, p.pid))
        
        for p in arrived_jobs:
            if len(self.active_queue) + (1 if self.current_process else 0) < self.max_active:
                p.state = "READY"
                self.active_queue.append(p)
                self.job_queue.remove(p)

        terminated_pid = None

        # 2. CPU SCHEDULER (Nivel 2): Round Robin sobre la active_queue
        if self.current_process:
            self.current_process.remaining_time -= 1
            self.current_q_time += 1

            if self.current_process.state == "TERMINATED" or self.current_process.remaining_time <= 0:
                self.current_process.state = "TERMINATED"
                self._calculate_metrics(self.current_process, current_time + 1)
                self.completed_processes.append(self.current_process)
                terminated_pid = self.current_process.pid
                self.current_process = None
                self.current_q_time = 0
            elif self.current_q_time >= self.quantum:
                self.current_process.state = "READY"
                self.active_queue.append(self.current_process)
                self.current_process = None
                self.current_q_time = 0

        if self.current_process is None and self.active_queue:
            self.current_process = self.active_queue.pop(0)
            self.current_process.state = "RUNNING"
            if self.current_process.start_time == -1:
                self.current_process.start_time = current_time

        return terminated_pid