# gui/bitmap_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QGridLayout, QMessageBox, QProgressBar, QLineEdit)
from PySide6.QtCore import Qt, QTimer

class BitmapWidget(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.sim = kernel.memory_manager.bitmap_sim
        self.next_pid = 1 # PID local para el simulador
        
        layout = QVBoxLayout(self)

        # --- PANEL DE CONFIGURACIÓN ---
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel(f"Memoria Total: {self.sim.total_memory} MB"))
        
        config_layout.addWidget(QLabel("Unidad de Asignación (MB):"))
        self.spin_unit = QSpinBox()
        self.spin_unit.setRange(1, self.sim.total_memory)
        self.spin_unit.setValue(4)
        config_layout.addWidget(self.spin_unit)
        
        self.btn_config = QPushButton("Configurar y Limpiar")
        self.btn_config.clicked.connect(self.configure_sim)
        config_layout.addWidget(self.btn_config)
        
        layout.addLayout(config_layout)

        # --- PANEL DE PROCESOS ---
        proc_layout = QHBoxLayout()
        proc_layout.addWidget(QLabel("Nombre/PID:"))
        self.in_name = QLineEdit(f"P{self.next_pid}")
        proc_layout.addWidget(self.in_name)
        
        proc_layout.addWidget(QLabel("Memoria (MB):"))
        self.spin_mem = QSpinBox()
        self.spin_mem.setRange(1, self.sim.total_memory)
        self.spin_mem.setValue(5)
        proc_layout.addWidget(self.spin_mem)
        
        proc_layout.addWidget(QLabel("Tiempo:"))
        self.spin_time = QSpinBox()
        self.spin_time.setRange(1, 999)
        self.spin_time.setValue(15)
        proc_layout.addWidget(self.spin_time)
        
        self.btn_add = QPushButton("Lanzar Proceso")
        self.btn_add.clicked.connect(self.add_process)
        self.btn_add.setEnabled(False) # Se habilita tras configurar
        proc_layout.addWidget(self.btn_add)
        
        layout.addLayout(proc_layout)

        # --- VISTA DIVIDIDA (Tabla y Cuadrícula) ---
        view_layout = QHBoxLayout()
        
        # Tabla de procesos
        table_layout = QVBoxLayout()
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["PID", "Nombre", "Memoria", "Tiempo Restante"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        table_layout.addWidget(self.table)
        
        self.btn_kill = QPushButton("Terminar Proceso Seleccionado")
        self.btn_kill.clicked.connect(self.kill_process)
        self.btn_kill.setEnabled(False)
        table_layout.addWidget(self.btn_kill)
        
        view_layout.addLayout(table_layout, 1)

        # Cuadrícula Visual 10x10 (Máximo 100 celdas)
        grid_container = QWidget()
        self.grid = QGridLayout(grid_container)
        self.grid.setSpacing(2)
        view_layout.addWidget(grid_container, 2)
        
        layout.addLayout(view_layout)

        self.kernel.events.subscribe("SYSTEM_TICK", self.refresh_views)

    def configure_sim(self):
        unit = self.spin_unit.value()
        if self.sim.total_memory // unit > 100:
            QMessageBox.warning(self, "Límite Excedido", "La unidad de asignación es muy pequeña. Generaría más de 100 celdas (Máximo 10x10).")
            return
            
        if self.sim.configure(unit):
            self.btn_add.setEnabled(True)
            self.btn_kill.setEnabled(True)
            self.refresh_views()
            self.next_pid = 1
            self.in_name.setText(f"P{self.next_pid}")

    def add_process(self):
        name = self.in_name.text()
        mem = self.spin_mem.value()
        time = self.spin_time.value()
        
        if self.sim.allocate(self.next_pid, name, mem, time):
            self.next_pid += 1
            self.in_name.setText(f"P{self.next_pid}")
            self.refresh_views()
        else:
            QMessageBox.warning(self, "Fallo de Asignación", "No hay suficientes celdas contiguas para este proceso.")

    def kill_process(self):
        selected = self.table.selectedItems()
        if not selected: return
        pid = int(self.table.item(selected[0].row(), 0).text())
        if self.sim.release(pid):
            self.refresh_views()

    def refresh_views(self, data=None):
        # 1. Actualizar Tabla
        procesos = list(self.sim.processes.items())
        self.table.setRowCount(len(procesos))
        for row, (pid, p) in enumerate(procesos):
            self.table.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(row, 1, QTableWidgetItem(p["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{p['required_memory']} MB"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{p['remaining_time']} t"))

        # 2. Actualizar Cuadrícula
        # Limpiamos el grid
        for i in reversed(range(self.grid.count())): 
            widget = self.grid.itemAt(i).widget()
            if widget: widget.deleteLater()
            
        # Dibujamos las celdas
        for i, cell in enumerate(self.sim.cells):
            row, col = divmod(i, 10) # Reparte en filas de máximo 10
            
            bar = QProgressBar()
            bar.setMinimum(0)
            bar.setMaximum(self.sim.allocation_unit)
            bar.setValue(cell["used_mb"])
            bar.setFormat("1" if cell["state"] == 1 else "0")
            bar.setAlignment(Qt.AlignCenter)
            bar.setFixedHeight(30)
            
            # CSS Mágico: Fondo Verde, Relleno Rojo
            bar.setStyleSheet("""
                QProgressBar {
                    background-color: #2ecc71; 
                    color: white; 
                    font-weight: bold; 
                    border: 1px solid #27ae60;
                }
                QProgressBar::chunk { background-color: #e74c3c; }
            """)
            
            self.grid.addWidget(bar, row, col)