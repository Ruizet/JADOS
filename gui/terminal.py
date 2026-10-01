# gui/terminal.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PySide6.QtGui import QFont, QColor, QTextCursor

class Terminal(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.setWindowTitle("Terminal - JADOS")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        
        # Área de salida
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: #000000; color: #00FF00; border: none; padding: 5px;")
        font = QFont("Consolas", 11)
        font.setBold(True)
        self.output.setFont(font)
        layout.addWidget(self.output)
        
        # Área de entrada
        self.input = QLineEdit()
        self.input.setStyleSheet("background-color: #000000; color: #FFFFFF; border: 1px solid #333333; padding: 2px;")
        self.input.setFont(font)
        layout.addWidget(self.input)
        
        self.input.returnPressed.connect(self.process_command)
        
        self.print_text("JADOS Terminal v3.0 - Core System")
        self.print_text("Escribe 'help' para ver la lista de comandos.\n")
        
        if not self.kernel.scheduler_configured:
            self.print_text("Atención: Debes configurar el planificador de CPU antes de iniciar el sistema.", color="#FFFF55")
            self.print_text("Usa el comando 'scheduler list' y 'scheduler select <id>'.", color="#AAAAAA")

    def print_text(self, text, color="#00FF00"):
        self.output.setTextColor(QColor(color))
        self.output.append(text)
        self.output.moveCursor(QTextCursor.End)

    def process_command(self):
        cmd_line = self.input.text().strip()
        if not cmd_line:
            return
            
        self.input.clear()
        self.print_text(f"root@JADOS:~# {cmd_line}", color="#FFFFFF")
        
        parts = cmd_line.split()
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == "help":
            self.cmd_help()
        elif cmd == "scheduler":
            self.cmd_scheduler(args)
        elif cmd == "boot":
            self.cmd_boot()
        elif cmd == "shutdown":
            self.cmd_shutdown()
        elif cmd == "run":
            self.cmd_run(args)
        elif cmd == "kill":
            self.cmd_kill(args)
        elif cmd == "ps":
            self.cmd_ps()
        elif cmd == "mem":
            self.cmd_mem()
        elif cmd == "clear":
            self.output.clear()
        else:
            self.print_text(f"Comando no reconocido: '{cmd}'. Escribe 'help'.", color="#FF5555")

    def cmd_help(self):
        help_text = (
            "Comandos disponibles:\n"
            "  scheduler list           : Muestra algoritmos de planificación disponibles\n"
            "  scheduler select <id>    : Selecciona el algoritmo antes de arrancar\n"
            "  boot                     : Enciende el sistema operativo JADOS\n"
            "  shutdown                 : Apaga el sistema operativo\n"
            "  run <nom> <llegada> <raf>: Crea proceso (Ej: run P1 0 5)\n"
            "  kill <pid>               : Termina un proceso activo\n"
            "  ps                       : Muestra los procesos en el planificador\n"
            "  mem                      : Muestra el estado de la memoria global\n"
            "  clear                    : Limpia la pantalla\n"
            "  help                     : Muestra este mensaje"
        )
        self.print_text(help_text)

    def cmd_scheduler(self, args):
        if self.kernel.is_running:
            self.print_text("Error: JADOS está ejecutándose. Apaga para cambiar.", color="#FF5555")
            return
        if not args:
            self.print_text("Uso: scheduler list | scheduler select <id> [parametros...]", color="#FFFF55")
            return
            
        if args[0] == "list":
            self.print_text("Algoritmos de CPU disponibles:", color="#55FFFF")
            self.print_text("  1. FCFS")
            self.print_text("  2. SJF")
            self.print_text("  3. Round Robin (Params: quantum)")
            self.print_text("  4. Priority")
            self.print_text("  5. Multilevel Queues (Params: quantumQ0 quantumQ1)")
            self.print_text("  6. Guaranteed Scheduling")
            self.print_text("  7. Two-Level Scheduling (Params: max_activos quantum)")
            
        elif args[0] == "select" and len(args) >= 2:
            algo_id = args[1]
            if algo_id == "1": success, msg = self.kernel.configure_scheduler("FCFS", {})
            elif algo_id == "2": success, msg = self.kernel.configure_scheduler("SJF", {})
            elif algo_id == "3":
                if len(args) < 3: return self.print_text("Uso: scheduler select 3 <quantum>", color="#FF5555")
                success, msg = self.kernel.configure_scheduler("RR", {"quantum": int(args[2])})
            elif algo_id == "4": success, msg = self.kernel.configure_scheduler("PRIORITY", {})
            elif algo_id == "5":
                if len(args) < 4: return self.print_text("Uso: scheduler select 5 <q0> <q1>", color="#FF5555")
                success, msg = self.kernel.configure_scheduler("MLQ", {"q0": int(args[2]), "q1": int(args[3])})
            elif algo_id == "6": success, msg = self.kernel.configure_scheduler("GUARANTEED", {})
            elif algo_id == "7":
                if len(args) < 4: return self.print_text("Uso: scheduler select 7 <max_act> <quantum>", color="#FF5555")
                success, msg = self.kernel.configure_scheduler("TWO_LEVEL", {"max": int(args[2]), "quantum": int(args[3])})
            else:
                return self.print_text("ID inválido.", color="#FF5555")
                
            self.print_text(msg, color="#55FF55" if success else "#FF5555")

    def cmd_run(self, args):
        if not self.kernel.is_running: return self.print_text("Error: Kernel apagado.", color="#FF5555")
        if len(args) < 3: return self.print_text("Uso: run <nombre> <llegada> <rafaga> [prioridad] [cola_0_1_2] [pct_garantizado]", color="#FFFF55")
            
        name = args[0]
        try:
            arrival = int(args[1])
            burst = int(args[2])
            priority = int(args[3]) if len(args) > 3 else 0
            queue_level = int(args[4]) if len(args) > 4 else 0
            pct = float(args[5]) if len(args) > 5 else 0.0
            
            pid = self.kernel.process_manager.create_process(name, arrival, burst, priority, queue_level, pct)
            self.print_text(f"Proceso '{name}' (PID: {pid}) admitido en el planificador.", color="#55FF55")
        except ValueError:
            self.print_text("Error en formato de parámetros numéricos.", color="#FF5555")

    def cmd_boot(self):
        if self.kernel.is_running:
            self.print_text("JADOS ya se encuentra en ejecución.", color="#FFFF55")
            return
            
        if not self.kernel.scheduler_configured:
            self.print_text("Error crítico: No se ha seleccionado un algoritmo de planificación de CPU.", color="#FF5555")
            self.print_text("Usa 'scheduler list' y 'scheduler select <id>' antes de iniciar.", color="#FFFF55")
            return
            
        self.kernel.is_running = True
        self.print_text("JADOS iniciando... [OK]", color="#55FF55")

    def cmd_shutdown(self):
        if not self.kernel.is_running:
            self.print_text("El sistema ya está apagado.", color="#FFFF55")
        else:
            self.kernel.is_running = False
            self.print_text("JADOS apagado de forma segura.", color="#55FF55")

    def cmd_kill(self, args):
        if not self.kernel.is_running:
            self.print_text("Error: El sistema está apagado.", color="#FF5555")
            return
            
        if len(args) != 1:
            self.print_text("Uso: kill <pid>", color="#FFFF55")
            return
            
        try:
            pid = int(args[0])
            if pid in self.kernel.process_manager.processes:
                self.kernel.process_manager.processes[pid].state = "TERMINATED"
                self.print_text(f"Proceso [{pid}] marcado como TERMINADO.", color="#55FF55")
            else:
                self.print_text(f"No se encontró un proceso con el PID {pid}.", color="#FF5555")
        except ValueError:
            self.print_text("Error: El PID debe ser un número entero.", color="#FF5555")

    def cmd_ps(self):
        if not self.kernel.is_running:
            self.print_text("Error: El sistema está apagado.", color="#FF5555")
            return
            
        procesos = self.kernel.process_manager.processes
        if not procesos:
            self.print_text("No hay procesos registrados en JADOS.")
        else:
            self.print_text(f"{'PID':<5} | {'NOMBRE':<10} | {'ESTADO':<10} | {'LLEGADA':<8} | {'RAFAGA':<8} | {'RESTANTE'}")
            self.print_text("-" * 65)
            for pid, p in procesos.items():
                self.print_text(f"{pid:<5} | {p.name:<10} | {p.state:<10} | {p.arrival_time:<8} | {p.burst_time:<8} | {p.remaining_time}")

    def cmd_mem(self):
        if not self.kernel.is_running:
            self.print_text("Error: El sistema está apagado.", color="#FF5555")
            return
        
        self.print_text("--- ARQUITECTURA DE MEMORIA JADOS ---", color="#55FFFF")
        self.print_text("La memoria global de 1024 MB está fragmentada en 4 entornos aislados:")
        self.print_text("  1. Sandbox: Mapa de Bits")
        self.print_text("  2. Sandbox: Listas Ligadas")
        self.print_text("  3. Sandbox: Buddy System")
        self.print_text("  4. Sandbox: Memoria Virtual (Paginación)")
        self.print_text("Utiliza la aplicación 'Memoria' en el escritorio para gestionar cada entorno.", color="#AAAAAA")