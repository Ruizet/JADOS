# gui/buddy_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLineEdit, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QTimer
import random

class BuddyWidget(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.sim = kernel.memory_manager.buddy_sim
        self.next_pid = 1
        self.process_colors = {}
        
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
        
        self.btn_add = QPushButton("Lanzar Proceso")
        self.btn_add.clicked.connect(self.add_process)
        input_layout.addWidget(self.btn_add)
        
        layout.addLayout(input_layout)

        # --- BARRA DE BLOQUES BUDDY ---
        self.lbl_bar_title = QLabel(f"Asignación por Bloques Buddy ({self.sim.total_memory} MB)")
        self.lbl_bar_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.lbl_bar_title)

        self.bar_container = QFrame()
        self.bar_container.setFixedHeight(75)
        self.bar_container.setStyleSheet("background-color: #ecf0f1; border: 2px solid #34495e; border-radius: 5px;")
        
        self.bar_layout = QHBoxLayout(self.bar_container)
        self.bar_layout.setContentsMargins(0, 0, 0, 0)
        self.bar_layout.setSpacing(0)
        layout.addWidget(self.bar_container)

        # --- TABLA DE PROCESOS ---
        table_layout = QHBoxLayout()
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["PID", "Nombre", "Solicitado", "Asignado", "Frag. Interna", "Tiempo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        table_layout.addWidget(self.table)
        layout.addLayout(table_layout)

        self.btn_kill = QPushButton("Terminar Proceso Seleccionado")
        self.btn_kill.clicked.connect(self.kill_process)
        layout.addWidget(self.btn_kill)

        self.kernel.events.subscribe("SYSTEM_TICK", self.refresh_views)

    def get_color_for_pid(self, pid):
        if pid not in self.process_colors:
            colors = ["#2ecc71", "#3498db", "#9b59b6", "#e67e22", "#e74c3c", "#1abc9c", "#d35400"]
            self.process_colors[pid] = random.choice(colors)
        return self.process_colors[pid]

    def add_process(self):
        name = self.in_name.text()
        mem = self.spin_mem.value()
        time = self.spin_time.value()
        
        if self.sim.allocate(self.next_pid, name, mem, time):
            self.next_pid += 1
            self.in_name.setText(f"P{self.next_pid}")
            self.refresh_views()
        else:
            QMessageBox.warning(self, "Fallo", "Memoria insuficiente o bloque contiguo no disponible.")

    def kill_process(self):
        selected = self.table.selectedItems()
        if not selected: return
        pid = int(self.table.item(selected[0].row(), 0).text())
        if self.sim.release(pid):
            self.refresh_views()

    def refresh_views(self, data=None):
        procesos = list(self.sim.processes.items())
        self.table.setRowCount(len(procesos))
        for row, (pid, p) in enumerate(procesos):
            self.table.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(row, 1, QTableWidgetItem(p["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{p['req_mem']} MB"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{p['alloc_mem']} MB"))
            frag_item = QTableWidgetItem(f"{p['frag']} MB")
            frag_item.setForeground(Qt.red if p['frag'] > 0 else Qt.black)
            self.table.setItem(row, 4, frag_item)
            self.table.setItem(row, 5, QTableWidgetItem(f"{p['remaining_time']} t"))

        while self.bar_layout.count():
            item = self.bar_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
                
        for block in self.sim.blocks:
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignCenter)
            
            if block.is_free:
                lbl.setStyleSheet("background-color: transparent; border-right: 1px solid #7f8c8d; color: #7f8c8d;")
                lbl.setText(f"{block.size} MB\n(Libre)")
            else:
                color = self.get_color_for_pid(block.pid)
                name = self.sim.processes[block.pid]["name"]
                lbl.setStyleSheet(f"background-color: {color}; color: white; border: 1px solid #2c3e50; font-weight: bold;")
                # Muestra el nombre, tamaño asignado y tamaño requerido
                lbl.setText(f"{name}\n{block.size} MB\n(Usa {block.req_mem} MB)")
            
            self.bar_layout.addWidget(lbl, block.size)