# process/scheduling/scheduler.py
class Scheduler:
    def __init__(self):
        self.ready_queue = []
        self.current_process = None
        self.completed_processes = []

    def add_process(self, process):
        process.state = "READY"
        self.ready_queue.append(process)

    def tick(self, current_time: int):
        """Método base. Debe ser sobrescrito por cada algoritmo."""
        raise NotImplementedError
        
    def _calculate_metrics(self, process, current_time):
        process.completion_time = current_time
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time