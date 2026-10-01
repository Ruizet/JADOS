# gui/linked_list_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QComboBox, QLineEdit, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QTimer
import random

class LinkedListWidget(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.sim = kernel.memory_manager.linked_list_sim
        self.next_pid = 1
        self.process_colors = {} # Diccionario para guardar el color asignado a cada PID
        
        layout = QVBoxLayout(self)

        # --- PANEL DE ENTRADA ---
        input_layout = QHBoxLayout()
        
        input_layout.addWidget(QLabel("Nombre/PID:"))
        self.in_name = QLineEdit(f"P{self.next_pid}")
        input_layout.addWidget(self.in_name)
        
        input_layout.addWidget(QLabel("Memoria (MB):"))
        self.spin_mem = QSpinBox()
        self.spin_mem.setRange(1, self.sim.total_memory)
        self.spin_mem.setValue(50)
        input_layout.addWidget(self.spin_mem)
        
        input_layout.addWidget(QLabel("Tiempo:"))
        self.spin_time = QSpinBox()
        self.spin_time.setRange(1, 999)
        self.spin_time.setValue(15)
        input_layout.addWidget(self.spin_time)

        input_layout.addWidget(QLabel("Algoritmo:"))
        self.combo_fit = QComboBox()
        self.combo_fit.addItems(["First Fit", "Next Fit", "Best Fit", "Worst Fit"])
        input_layout.addWidget(self.combo_fit)
        
        self.btn_add = QPushButton("Lanzar Proceso")
        self.btn_add.clicked.connect(self.add_process)
        input_layout.addWidget(self.btn_add)
        
        layout.addLayout(input_layout)

        # --- BARRA HORIZONTAL DE MEMORIA ---
        self.lbl_bar_title = QLabel(f"Barra de Memoria ({self.sim.total_memory} MB Totales)")
        self.lbl_bar_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.lbl_bar_title)

        # Contenedor de la barra
        self.bar_container = QFrame()
        self.bar_container.setFixedHeight(70) # Barra gruesa
        self.bar_container.setStyleSheet("background-color: #ecf0f1; border: 2px solid #7f8c8d; border-radius: 5px;")
        
        self.bar_layout = QHBoxLayout(self.bar_container)
        self.bar_layout.setContentsMargins(0, 0, 0, 0)
        self.bar_layout.setSpacing(0)
        layout.addWidget(self.bar_container)

        # --- TABLA DE PROCESOS ---
        table_layout = QHBoxLayout()
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["PID", "Nombre", "Memoria", "Tiempo", "Fit Usado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        table_layout.addWidget(self.table)
        layout.addLayout(table_layout)

        self.btn_kill = QPushButton("Terminar Proceso Seleccionado")
        self.btn_kill.clicked.connect(self.kill_process)
        layout.addWidget(self.btn_kill)

        # Timer local
        self.kernel.events.subscribe("SYSTEM_TICK", self.refresh_views)

    def get_color_for_pid(self, pid):
        """Asigna y recuerda un color aleatorio (oscuro para buen contraste) por proceso."""
        if pid not in self.process_colors:
            colors = ["#e74c3c", "#3498db", "#9b59b6", "#e67e22", "#16a085", "#2980b9", "#d35400", "#c0392b"]
            self.process_colors[pid] = random.choice(colors)
        return self.process_colors[pid]

    def add_process(self):
        name = self.in_name.text()
        mem = self.spin_mem.value()
        time = self.spin_time.value()
        fit = self.combo_fit.currentText()
        
        if self.sim.allocate(self.next_pid, name, mem, time, fit):
            self.next_pid += 1
            self.in_name.setText(f"P{self.next_pid}")
            self.refresh_views()
        else:
            QMessageBox.warning(self, "Fallo de Asignación", f"No se pudo asignar memoria usando {fit}. La fragmentación externa puede ser la causa.")

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
            self.table.setItem(row, 4, QTableWidgetItem(p["fit_type"]))

        # 2. Actualizar Barra de Memoria (Listas Ligadas visuales)
        # Limpiar bloques anteriores
        while self.bar_layout.count():
            item = self.bar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Dibujar bloques reales
        for block in self.sim.blocks:
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignCenter)
            
            if block.is_free:
                lbl.setStyleSheet("background-color: rgba(189, 195, 199, 0.5); border-right: 1px solid #7f8c8d; color: #34495e;")
                lbl.setText(f"Libre\n{block.size} MB")
            else:
                color = self.get_color_for_pid(block.pid)
                fit = self.sim.processes[block.pid]["fit_type"]
                name = self.sim.processes[block.pid]["name"]
                lbl.setStyleSheet(f"background-color: {color}; color: white; border-right: 1px solid #2c3e50; font-weight: bold;")
                lbl.setText(f"{name}\n{block.size} MB\n({fit})")
            
            # MAGIA: Usamos el tamaño del bloque como 'stretch factor' (peso proporcional)
            self.bar_layout.addWidget(lbl, block.size)