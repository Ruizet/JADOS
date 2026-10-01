# process/process.py
class Process:
    def __init__(self, pid: int, name: str, arrival_time: int, burst_time: int, priority: int = 0, queue_level: int = 0, guaranteed_pct: float = 0.0):
        self.pid = pid
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.queue_level = queue_level
        self.guaranteed_pct = guaranteed_pct
        
        # Estado de ejecución
        self.remaining_time = burst_time
        self.state = "NEW" # NEW, READY, RUNNING, WAITING, TERMINATED
        
        # Métricas
        self.start_time = -1
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = 0