# process/scheduling/multilevel_queue.py
from process.scheduling.scheduler import Scheduler

class MultilevelQueueScheduler(Scheduler):
    def __init__(self, q0_quantum: int, q1_quantum: int):
        super().__init__()
        self.q0_quantum = q0_quantum
        self.q1_quantum = q1_quantum
        self.current_q_time = 0
        self.unstarted = []

    def add_process(self, process):
        process.state = "NEW"
        self.unstarted.append(process)

    def tick(self, current_time: int):
        # 1. Admitir procesos nuevos
        for p in [p for p in self.unstarted if p.arrival_time <= current_time]:
            p.state = "READY"
            self.ready_queue.append(p)
            self.unstarted.remove(p)

        terminated_pid = None

        # 2. Ejecutar y controlar el Quantum del proceso actual
        if self.current_process:
            self.current_process.remaining_time -= 1
            self.current_q_time += 1
            
            # Forzamos terminación si fue matado por Task Manager
            if self.current_process.state == "TERMINATED" or self.current_process.remaining_time <= 0:
                self.current_process.state = "TERMINATED"
                self._calculate_metrics(self.current_process, current_time + 1)
                self.completed_processes.append(self.current_process)
                terminated_pid = self.current_process.pid
                self.current_process = None
                self.current_q_time = 0
            else:
                # Verificamos si se le acabó el quantum (solo si está en Q0 o Q1)
                lvl = self.current_process.queue_level
                if (lvl == 0 and self.current_q_time >= self.q0_quantum) or \
                   (lvl == 1 and self.current_q_time >= self.q1_quantum):
                    self.current_process.state = "READY"
                    self.ready_queue.append(self.current_process)
                    self.current_process = None
                    self.current_q_time = 0

        # 3. Seleccionar siguiente proceso (Prioridad estricta: Q0 -> Q1 -> Q2)
        if self.current_process is None and self.ready_queue:
            # Separamos en colas virtuales momentáneas
            q0 = [p for p in self.ready_queue if p.queue_level == 0]
            q1 = [p for p in self.ready_queue if p.queue_level == 1]
            q2 = [p for p in self.ready_queue if p.queue_level == 2]

            if q0: next_p = q0[0]
            elif q1: next_p = q1[0]
            elif q2: next_p = q2[0]
            else: next_p = None

            if next_p:
                self.current_process = next_p
                self.ready_queue.remove(self.current_process)
                self.current_process.state = "RUNNING"
                if self.current_process.start_time == -1:
                    self.current_process.start_time = current_time
                    self.current_process.response_time = current_time - self.current_process.arrival_time

        return terminated_pid