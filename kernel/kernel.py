# kernel/kernel.py
from kernel.events import EventBus
from process.process_manager import ProcessManager
from memory.memory_manager import MemoryManager
from filesystem.filesystem import FileSystem

class Kernel:
    def __init__(self):
        self.system_clock = 0
        self.is_running = False
        self.scheduler_configured = False # Bloqueo para obligar a configurar antes del boot
        
        self.events = EventBus()
        self.process_manager = ProcessManager()
        self.memory_manager = MemoryManager() # La memoria ahora se autogestiona
        self.fs = FileSystem()

    def configure_scheduler(self, algorithm_name: str, params: dict):
        if self.is_running:
            return False, "JADOS ya está en ejecución. Reinicia para cambiar el planificador."
            
        try:
            if algorithm_name == "FCFS":
                from process.scheduling.fcfs import FCFSScheduler
                self.process_manager.set_scheduler(FCFSScheduler())
            elif algorithm_name == "SJF":
                from process.scheduling.sjf import SJFScheduler
                self.process_manager.set_scheduler(SJFScheduler())
            elif algorithm_name == "RR":
                from process.scheduling.round_robin import RoundRobinScheduler
                self.process_manager.set_scheduler(RoundRobinScheduler(params.get("quantum", 2)))
            elif algorithm_name == "PRIORITY":
                from process.scheduling.priority import PriorityScheduler
                self.process_manager.set_scheduler(PriorityScheduler())
            elif algorithm_name == "MLQ":
                from process.scheduling.multilevel_queue import MultilevelQueueScheduler
                self.process_manager.set_scheduler(MultilevelQueueScheduler(params.get("q0", 3), params.get("q1", 6)))
            elif algorithm_name == "GUARANTEED":
                from process.scheduling.guaranteed import GuaranteedScheduler
                self.process_manager.set_scheduler(GuaranteedScheduler())
            elif algorithm_name == "TWO_LEVEL":
                from process.scheduling.two_level import TwoLevelScheduler
                self.process_manager.set_scheduler(TwoLevelScheduler(params.get("max", 3), params.get("quantum", 4)))
            else:
                return False, "Algoritmo no soportado o en desarrollo."
                
            self.scheduler_configured = True
            return True, f"Planificador {algorithm_name} configurado exitosamente."
        except ImportError as e:
            return False, f"Falta el archivo del algoritmo: {e}"

    def tick(self):
        """Avanza el reloj central del sistema operativo."""
        if self.is_running:
            # 1. Ciclo de CPU (Planificador)
            terminated_pid = self.process_manager.execute_cycle(self.system_clock)
            
            # 2. Ciclo de Memoria (Para los simuladores que lo requieran)
            self.memory_manager.tick()
            
            # 3. Avanzar reloj y notificar a la interfaz gráfica
            self.system_clock += 1
            self.events.publish("SYSTEM_TICK")