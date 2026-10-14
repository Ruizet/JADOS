# gui/io_window.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLabel, 
                               QLineEdit, QComboBox, QSplitter, QGridLayout, QFrame)
from PySide6.QtCore import Qt, QThread, Signal, QTimer

class ScannerThread(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, device_manager):
        super().__init__()
        self.device_manager = device_manager

    def run(self):
        try:
            devices = self.device_manager.scan_hardware()
            self.finished.emit(devices)
        except Exception as e:
            self.error.emit(str(e))

class IOWindow(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.setWindowTitle("Administración de E/S - JADOS")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        self.all_devices = []
        self.scanner_thread = None
        
        self._setup_ui()
        
        self.trigger_background_scan()
        
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self.trigger_background_scan)
        self.auto_refresh_timer.start(3000)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- BARRA SUPERIOR ---
        toolbar = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Buscar dispositivo...")
        self.search_box.setMinimumHeight(30)
        self.search_box.textChanged.connect(self.filter_table)
        
        self.combo_category = QComboBox()
        self.combo_category.setMinimumHeight(30)
        self.combo_category.addItems(["Todas las categorías", "Entrada", "Audio", "Cámaras e imagen", 
                                      "Almacenamiento", "Bluetooth", "Pantallas y monitores", "Otros"])
        self.combo_category.currentTextChanged.connect(self.filter_table)

        toolbar.addWidget(self.search_box)
        toolbar.addWidget(self.combo_category)
        main_layout.addLayout(toolbar)

        # --- DIVISOR PRINCIPAL (Ahora Vertical) ---
        splitter = QSplitter(Qt.Vertical)
        
        # 1. TABLA (Ocupará todo el ancho)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nombre", "Categoría", "Conexión", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Mejoras visuales en la tabla (Filas más altas, texto más grande)
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.verticalHeader().setVisible(False) # Ocultar números de fila para más limpieza
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3e50; 
                alternate-background-color: #34495e;
                font-size: 13px;
                gridline-color: #1a252f;
            }
            QHeaderView::section {
                background-color: #1a252f;
                padding: 5px;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #2c3e50;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.show_details)
        splitter.addWidget(self.table)
        
        # 2. PANEL DE DETALLES (Inferior, distribuido a lo ancho)
        details_frame = QFrame()
        details_frame.setStyleSheet("background-color: #2c3e50; border-radius: 5px;")
        self.details_layout = QGridLayout(details_frame)
        self.details_layout.setSpacing(10)
        self.details_layout.setContentsMargins(15, 15, 15, 15)
        
        self.lbl_det_name = QLabel("-")
        self.lbl_det_manuf = QLabel("-")
        self.lbl_det_conn = QLabel("-")
        self.lbl_det_drv_name = QLabel("-")
        self.lbl_det_drv_prov = QLabel("-")
        self.lbl_det_drv_ver = QLabel("-")
        self.lbl_det_id = QLabel("-")
        
        # Hacemos que el ID pueda tener varias líneas si es muy largo
        self.lbl_det_id.setWordWrap(True)
        
        # Función rápida para crear títulos bonitos
        def make_title(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #85c1e9; font-weight: bold;")
            return lbl

        # Fila 0
        self.details_layout.addWidget(make_title("Dispositivo:"), 0, 0)
        self.details_layout.addWidget(self.lbl_det_name, 0, 1)
        self.details_layout.addWidget(make_title("Fabricante:"), 0, 2)
        self.details_layout.addWidget(self.lbl_det_manuf, 0, 3)

        # Fila 1
        self.details_layout.addWidget(make_title("Controlador:"), 1, 0)
        self.details_layout.addWidget(self.lbl_det_drv_name, 1, 1)
        self.details_layout.addWidget(make_title("Proveedor:"), 1, 2)
        self.details_layout.addWidget(self.lbl_det_drv_prov, 1, 3)

        # Fila 2
        self.details_layout.addWidget(make_title("Conexión:"), 2, 0)
        self.details_layout.addWidget(self.lbl_det_conn, 2, 1)
        self.details_layout.addWidget(make_title("Versión Drv:"), 2, 2)
        self.details_layout.addWidget(self.lbl_det_drv_ver, 2, 3)

        # Fila 3
        self.details_layout.addWidget(make_title("Hardware ID:"), 3, 0)
        self.details_layout.addWidget(self.lbl_det_id, 3, 1, 1, 3) # Expande 3 columnas
        
        splitter.addWidget(details_frame)
        
        # Asignar proporción (75% tabla, 25% panel inferior)
        splitter.setSizes([450, 150])
        main_layout.addWidget(splitter)
        
        # --- ESTADO INFERIOR ---
        self.lbl_status = QLabel("Iniciando...")
        self.lbl_status.setMinimumHeight(20)
        main_layout.addWidget(self.lbl_status)

    def trigger_background_scan(self):
        if not self.kernel.is_running:
            self.lbl_status.setText("🔴 Sin energía en los puertos. Enciende JADOS (boot) para detectar hardware.")
            self.lbl_status.setStyleSheet("color: #ff5555; font-weight: bold;")
            self.all_devices = []
            self.filter_table()
            return
            
        self.lbl_status.setStyleSheet("color: #aeb6bf;")
            
        if self.scanner_thread and self.scanner_thread.isRunning():
            return
            
        self.scanner_thread = ScannerThread(self.kernel.device_manager)
        self.scanner_thread.finished.connect(self.on_scan_complete)
        self.scanner_thread.error.connect(self.on_scan_error)
        self.scanner_thread.start()

    def on_scan_complete(self, devices):
        current_ids = {d["device_id"] for d in self.all_devices}
        new_ids = {d["device_id"] for d in devices}
        
        if current_ids != new_ids or not self.all_devices:
            self.all_devices = devices
            self.filter_table()
            self.lbl_status.setText(f"✅ Monitoreo activo: {len(devices)} dispositivos conectados.")

    def on_scan_error(self, err_msg):
        self.lbl_status.setText(f"⚠️ Monitoreo pausado (Error WMI): {err_msg}")

    def filter_table(self):
        search_text = self.search_box.text().lower()
        category_text = self.combo_category.currentText()
        
        selected_id = None
        selected_items = self.table.selectedItems()
        if selected_items:
            selected_id = self.table.item(selected_items[0].row(), 0).data(Qt.UserRole)["device_id"]
        
        filtered = []
        for d in self.all_devices:
            match_cat = (category_text == "Todas las categorías" or d["category"] == category_text)
            match_search = (search_text in d["name"].lower() or search_text in d["device_id"].lower())
            if match_cat and match_search:
                filtered.append(d)
                
        self.table.setRowCount(len(filtered))
        row_to_select = -1
        
        for row, d in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(d["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(d["category"]))
            self.table.setItem(row, 2, QTableWidgetItem(d["connection"]))
            
            status_item = QTableWidgetItem(d["status"])
            if d["status"] == "OK": status_item.setForeground(Qt.green)
            else: status_item.setForeground(Qt.yellow)
            self.table.setItem(row, 3, status_item)
            
            self.table.item(row, 0).setData(Qt.UserRole, d)
            
            if d["device_id"] == selected_id:
                row_to_select = row

        if row_to_select >= 0:
            self.table.selectRow(row_to_select)

    def show_details(self):
        selected = self.table.selectedItems()
        if not selected: 
            self._clear_details()
            return
        
        d = self.table.item(selected[0].row(), 0).data(Qt.UserRole)
        self.lbl_det_name.setText(d["name"])
        self.lbl_det_manuf.setText(d["manufacturer"])
        self.lbl_det_conn.setText(d["connection"])
        self.lbl_det_drv_name.setText(d["driver_name"])
        self.lbl_det_drv_prov.setText(d["driver_provider"])
        self.lbl_det_drv_ver.setText(d["driver_version"])
        self.lbl_det_id.setText(d["device_id"])
        
    def _clear_details(self):
        for lbl in [self.lbl_det_name, self.lbl_det_manuf, self.lbl_det_conn, 
                    self.lbl_det_drv_name, self.lbl_det_drv_prov, self.lbl_det_drv_ver, self.lbl_det_id]:
            lbl.setText("-")