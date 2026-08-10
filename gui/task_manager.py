# gui/task_manager.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox

class TaskManager(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.setWindowTitle("Administrador de Tareas")
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 6) 
        self.table.setHorizontalHeaderLabels(["PID", "Proceso", "Estado", "Prioridad", "Memoria", "Tiempo"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_kill = QPushButton("Finalizar Proceso")
        self.btn_kill.clicked.connect(self._kill_selected_process)
        btn_layout.addWidget(self.btn_kill)
        layout.addLayout(btn_layout)

        # FASE 9: Nos suscribimos al evento del Kernel en lugar de usar QTimer
        if self.kernel:
            self.kernel.events.subscribe("PROCESS_CHANGED", self._refresh_table)
            self._refresh_table()

    def _refresh_table(self, data=None):
        if not self.kernel or not self.kernel.process_manager:
            return
            
        procesos = self.kernel.process_manager.get_all_processes()
        self.table.setRowCount(len(procesos))
        
        for row, p in enumerate(procesos):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.pid)))
            self.table.setItem(row, 1, QTableWidgetItem(p.name))
            self.table.setItem(row, 2, QTableWidgetItem(p.state.value))
            self.table.setItem(row, 3, QTableWidgetItem(str(p.priority)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{p.memory_required} MB"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{p.remaining_time} / {p.total_time}"))

    def _kill_selected_process(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Seleccione un proceso primero.")
            return
            
        pid = int(self.table.item(selected_items[0].row(), 0).text())
        response = self.kernel.execute_command("kill", [str(pid)])
        
        if "Error" in response:
            QMessageBox.warning(self, "Error", response)
        # Ya no forzamos el refresco manual, el Kernel disparará el evento automáticamente.