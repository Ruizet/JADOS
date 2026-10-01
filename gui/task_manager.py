# gui/task_manager.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class TaskManager(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.setWindowTitle("Administrador de Tareas")
        
        layout = QVBoxLayout(self)
        
        self.lbl_algo = QLabel("Planificador de CPU: Ninguno")
        self.lbl_algo.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #2ecc71;")
        layout.addWidget(self.lbl_algo)
        
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["PID", "Nombre", "Estado", "Llegada", "Ráfaga", "Restante", "Prioridad"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        # --- NUEVO BOTÓN DE TERMINAR ---
        self.btn_kill = QPushButton("Terminar Proceso Seleccionado")
        self.btn_kill.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; padding: 8px;")
        self.btn_kill.clicked.connect(self.kill_selected_process)
        layout.addWidget(self.btn_kill)
        
        self.kernel.events.subscribe("SYSTEM_TICK", self._refresh_table)
        self._refresh_table()

    def kill_selected_process(self):
        selected = self.table.selectedItems()
        if not selected: return
        
        pid = int(self.table.item(selected[0].row(), 0).text())
        if pid in self.kernel.process_manager.processes:
            p = self.kernel.process_manager.processes[pid]
            if p.state not in ["TERMINATED"]:
                p.state = "TERMINATED"
                QMessageBox.information(self, "Proceso Terminado", f"El proceso {p.name} (PID: {p.pid}) ha sido terminado por el usuario.")
                self._refresh_table()

    def _refresh_table(self, data=None):
        if self.kernel.process_manager.scheduler:
            algo_name = self.kernel.process_manager.scheduler.__class__.__name__.replace("Scheduler", "")
            self.lbl_algo.setText(f"Planificador de CPU activo: {algo_name}")
        else:
            self.lbl_algo.setText("Planificador de CPU: No configurado (Usa la Terminal)")

        try: procesos = self.kernel.process_manager.get_all_processes()
        except AttributeError: procesos = []

        self.table.setRowCount(len(procesos))
        
        for row, p in enumerate(procesos):
            def _create_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                return item

            self.table.setItem(row, 0, _create_item(p.pid))
            self.table.setItem(row, 1, _create_item(p.name))
            
            state_item = _create_item(p.state)
            if p.state == "RUNNING": state_item.setForeground(Qt.green)
            elif p.state == "TERMINATED": state_item.setForeground(Qt.red)
            elif p.state == "READY": state_item.setForeground(Qt.blue)
            self.table.setItem(row, 2, state_item)
            
            self.table.setItem(row, 3, _create_item(p.arrival_time))
            self.table.setItem(row, 4, _create_item(p.burst_time))
            self.table.setItem(row, 5, _create_item(p.remaining_time))
            self.table.setItem(row, 6, _create_item(p.priority))