# gui/virtual_memory_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLineEdit, QTabWidget, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

class VirtualMemoryWidget(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.sim = kernel.memory_manager.page_replacement_sim
        
        layout = QVBoxLayout(self)

        # --- PANEL DE ENTRADA ---
        input_layout = QHBoxLayout()
        
        input_layout.addWidget(QLabel("Cadena:"))
        self.in_string = QLineEdit("1 2 4 2 5 4")
        input_layout.addWidget(self.in_string)
        
        input_layout.addWidget(QLabel("Marcos:"))
        self.spin_frames = QSpinBox()
        self.spin_frames.setRange(1, 10)
        self.spin_frames.setValue(3)
        input_layout.addWidget(self.spin_frames)

        # Campo de Limpieza (Solo visible en NRU)
        self.lbl_clean = QLabel("Limpieza NRU (pasos):")
        self.spin_clean = QSpinBox()
        self.spin_clean.setRange(1, 99)
        self.spin_clean.setValue(3)
        input_layout.addWidget(self.lbl_clean)
        input_layout.addWidget(self.spin_clean)
        
        self.btn_sim = QPushButton("Simular")
        self.btn_sim.clicked.connect(self.run_simulation)
        input_layout.addWidget(self.btn_sim)

        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.clicked.connect(self.clear_views)
        input_layout.addWidget(self.btn_clear)
        
        layout.addLayout(input_layout)

        # --- PESTAÑAS DE ALGORITMOS ---
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.algos = ["OPT", "NRU", "FIFO", "LRU"]
        self.tables = {} 
        self.labels_res = {} 

        for algo in self.algos:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            lbl_res = QLabel("Esperando simulación...")
            lbl_res.setStyleSheet("font-weight: bold; margin: 5px 0;")
            self.labels_res[algo] = lbl_res
            tab_layout.addWidget(lbl_res)

            table = QTableWidget(0, 0) 
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionMode(QTableWidget.NoSelection)
            self.tables[algo] = table
            tab_layout.addWidget(table)
            
            self.tabs.addTab(tab, algo)
            
        # Conectar cambio de pestaña para ocultar/mostrar Limpieza
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.on_tab_changed(0) 

    def on_tab_changed(self, index):
        if self.algos[index] == "NRU":
            self.lbl_clean.show()
            self.spin_clean.show()
        else:
            self.lbl_clean.hide()
            self.spin_clean.hide()

    def run_simulation(self):
        ref_str = self.in_string.text()
        frames = self.spin_frames.value()
        clean_time = self.spin_clean.value() 
        
        if not ref_str.strip():
            return

        for algo in self.algos:
            result = self.sim.simulate(algo, ref_str, frames, clean_time)
            if result:
                self._draw_table(algo, result, frames)

    def _create_item(self, text, fg_color=None, bold=False):
        """Helper para crear celdas. Ya NO fuerza colores de fondo, respeta el tema del SO."""
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignCenter)
        if fg_color:
            item.setForeground(QColor(fg_color))
        if bold:
            font = QFont()
            font.setBold(True)
            item.setFont(font)
        return item

    def _draw_table(self, algo: str, result: dict, frames: int):
        table = self.tables[algo]
        steps = result["steps"]
        table.clearSpans()
        
        # Configuración de Filas (Top a Bottom)
        num_rows = 2 + frames 
        table.setRowCount(num_rows)
        
        # Cabeceras verticales
        v_headers = ["Páginas"] + [f"Marco {i+1}" for i in range(frames)] + ["Fallo"]
        table.setVerticalHeaderLabels(v_headers)
        
        if algo != "NRU":
            # --- TABLA ESTÁNDAR (Transpuesta) ---
            table.setColumnCount(len(steps))
            table.setHorizontalHeaderLabels([str(s["step"]) for s in steps])
            
            for col, step in enumerate(steps):
                table.setItem(0, col, self._create_item(step["page"], bold=True))
                
                for r in range(frames):
                    table.setItem(r + 1, col, self._create_item(step["frames"][r]))
                
                fault = step["status_mark"]
                fg = "red" if fault == "F" else "green"
                table.setItem(num_rows - 1, col, self._create_item(fault, fg_color=fg, bold=True))
                
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                
        else:
            # --- TABLA NRU (Con columnas divididas R/M y eventos) ---
            total_cols = 0
            col_map = [] 
            for s in steps:
                col_map.append(total_cols)
                total_cols += 3 
                if s["is_clean"]:
                    total_cols += 1 
                    
            table.setColumnCount(total_cols)
            
            # Cabeceras Horizontales Personalizadas
            h_headers = []
            for s in steps:
                label = str(s["step"]) + ("*" if s["is_clean"] else "")
                h_headers.extend([label, "", ""])
                if s["is_clean"]:
                    h_headers.append("")
            table.setHorizontalHeaderLabels(h_headers)
            
            for i, step in enumerate(steps):
                base_col = col_map[i]
                
                # Fila de Páginas y cabeceras R M
                table.setItem(0, base_col, self._create_item(step["page"], bold=True))
                table.setItem(0, base_col + 1, self._create_item("R", bold=True))
                table.setItem(0, base_col + 2, self._create_item("M", bold=True))
                
                # Filas de los Marcos
                for r in range(frames):
                    f_data = step["frames"][r]
                    table.setItem(r + 1, base_col, self._create_item(f_data["val"]))
                    table.setItem(r + 1, base_col + 1, self._create_item(f_data["R"]))
                    table.setItem(r + 1, base_col + 2, self._create_item(f_data["M"]))
                
                # Fila de Fallos
                fault = step["status_mark"]
                fg = "red" if fault == "F" else "green"
                table.setItem(num_rows - 1, base_col, self._create_item(fault, fg_color=fg, bold=True))
                table.setSpan(num_rows - 1, base_col, 1, 3) 
                
                # Columna de Limpieza (Solo se dibuja texto en la primera fila)
                if step["is_clean"]:
                    clean_col = base_col + 3
                    table.setItem(0, clean_col, self._create_item("Limpiar R", fg_color="#3498db", bold=True))
                    # Rellenamos el resto de celdas vacías hacia abajo para que la cuadrícula se dibuje bien
                    for r in range(1, num_rows):
                        table.setItem(r, clean_col, self._create_item(""))
                    
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # Opcional: Permitir scroll horizontal si hay muchas columnas
            table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
            
        self.labels_res[algo].setText(
            f"Total de Fallos: {result['total_faults']} | Rendimiento: {100 - result['fault_rate']:.1f}%"
        )

    def clear_views(self):
        self.in_string.setText("")
        for algo in self.algos:
            self.tables[algo].setRowCount(0)
            self.labels_res[algo].setText("Esperando simulación...")