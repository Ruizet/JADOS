# kernel/kernel.py
from process.process_manager import ProcessManager
from memory.memory_manager import MemoryManager
from filesystem.filesystem import FileSystem
from kernel.events import EventBus

class Kernel:
    def __init__(self):
        self.is_running = False
        self.system_clock = 0
        
        self.events = EventBus() # <-- FASE 9: Bus de eventos
        
        self.process_manager = ProcessManager()
        self.memory_manager = MemoryManager(total_ram=1024)
        self.fs = FileSystem()

    def boot(self) -> str:
        if self.is_running: return "El sistema ya está en ejecución."
        self.is_running = True
        self.system_clock = 0
        self.events.publish("PROCESS_CHANGED") # Refrescar GUI
        return "[Kernel] Sistema iniciado correctamente."

    def shutdown(self) -> str:
        self.is_running = False
        self.events.publish("PROCESS_CHANGED") # Refrescar GUI
        return "[Kernel] Sistema apagado."

    def tick(self):
        if self.is_running:
            self.system_clock += 1
            terminated_pid = self.process_manager.execute_cycle()
            
            if terminated_pid is not None:
                self.memory_manager.release(terminated_pid)
            
            # Emitimos un evento cada tick para que la GUI actualice los tiempos sincronizadamente
            self.events.publish("PROCESS_CHANGED")

    def execute_command(self, cmd: str, args: list) -> str:
        if cmd == "boot": return self.boot()
        if not self.is_running: return "Error: El sistema está apagado. Ejecute 'boot'."
        if cmd == "shutdown": return self.shutdown()
        
        # --- PROCESOS ---
        if cmd == "run":
            if len(args) < 1: return "Error: Faltan argumentos. Uso: run <nombre> [memoria] [tiempo]"
            name, memory, time = args[0], int(args[1]) if len(args) > 1 else 128, int(args[2]) if len(args) > 2 else 10
            
            if self.memory_manager.allocate(self.process_manager.next_pid, memory):
                proc = self.process_manager.create_process(name, memory, time)
                self.events.publish("PROCESS_CHANGED") # Aviso de nuevo proceso
                return f"[Kernel] Proceso '{name}' creado (PID {proc.pid})."
            return f"Error: Memoria RAM insuficiente para '{name}'."

        elif cmd == "kill":
            if len(args) < 1: return "Error: Faltan argumentos."
            pid = int(args[0])
            if self.process_manager.kill_process(pid):
                self.memory_manager.release(pid)
                self.events.publish("PROCESS_CHANGED") # Aviso de proceso muerto
                return f"[Kernel] Proceso PID {pid} finalizado. Memoria liberada."
            return f"Error: No se pudo matar el PID {pid}."

        # (ps y mem se mantienen igual, solo retornan texto)
        elif cmd == "ps":
            procesos = self.process_manager.get_all_processes()
            if not procesos: return "No hay procesos."
            out = "PID\tNOMBRE\tESTADO\t\tMEM\tTIEMPO\n" + "-" * 55 + "\n"
            for p in procesos: out += f"{p.pid}\t{p.name}\t{p.state.value}\t\t{p.memory_required}MB\t{p.remaining_time}/{p.total_time}t\n"
            return out
            
        elif cmd == "mem":
            return f"[Kernel]\n{self.memory_manager.get_status()}"

        # --- FILESYSTEM ---
        elif cmd == "mkdir":
            if len(args) < 1: return "Error: Uso: mkdir <nombre_carpeta>"
            res = self.fs.create_directory(args[0])
            self.events.publish("FS_CHANGED") # Aviso de cambio en disco
            return res

        elif cmd == "touch":
            if len(args) < 1: return "Error: Uso: touch <archivo> [contenido]"
            res = self.fs.create_file(args[0], " ".join(args[1:]) if len(args) > 1 else "")
            self.events.publish("FS_CHANGED") # Aviso de cambio en disco
            return res

        elif cmd == "rm":
            if len(args) < 1: return "Error: Uso: rm <nombre>"
            res = self.fs.remove_element(args[0])
            self.events.publish("FS_CHANGED") # Aviso de cambio en disco
            return res

        # (ls, cat, cd se mantienen igual porque solo leen, no modifican)
        elif cmd == "ls": return self.fs.list_directory()
        elif cmd == "cat": return self.fs.read_file(args[0] if len(args) > 0 else "")
        elif cmd == "cd": return self.fs.change_directory(args[0] if len(args) > 0 else "")
        else: return f"Error: Comando '{cmd}' no reconocido."