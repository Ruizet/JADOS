# gui/memory_window.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt

class MemoryWindow(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.setWindowTitle("Monitor de Memoria (Particiones)")
        layout = QVBoxLayout(self)

        # Resumen de memoria
        self.lbl_summary = QLabel("Cargando estado de memoria...")
        self.lbl_summary.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(self.lbl_summary)

        # Tabla visual
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID Partición", "Tamaño Total", "Estado", "PID Asignado", "Desperdicio (Frag.)"])
        
        # Ajustar columnas automáticamente
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.table)

        # Nos suscribimos al evento del Kernel para redibujar la tabla en vivo
        if self.kernel:
            self.kernel.events.subscribe("PROCESS_CHANGED", self._refresh_view)
            self._refresh_view()

    def _refresh_view(self, data=None):
        if not self.kernel or not self.kernel.is_running:
            self.lbl_summary.setText("El sistema está apagado.")
            self.table.setRowCount(0)
            return
        
        raw_data = self.kernel.memory_manager.get_raw_data()
        self.table.setRowCount(len(raw_data))
        
        total_free = 0
        total_wasted = 0

        for row, part in enumerate(raw_data):
            is_free = part["is_free"]
            size = part["size"]
            frag = part["fragmentation"]
            
            if is_free:
                total_free += size
            else:
                total_wasted += frag

            # Llenamos las celdas
            self.table.setItem(row, 0, QTableWidgetItem(str(part["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(f"{size} MB"))
            
            estado_item = QTableWidgetItem("Libre" if is_free else "Ocupado")
            if not is_free:
                estado_item.setForeground(Qt.red)
            else:
                estado_item.setForeground(Qt.darkGreen)
            self.table.setItem(row, 2, estado_item)
            
            pid_str = str(part["pid"]) if not is_free else "-"
            self.table.setItem(row, 3, QTableWidgetItem(pid_str))
            
            frag_str = f"{frag} MB" if not is_free else "0 MB"
            self.table.setItem(row, 4, QTableWidgetItem(frag_str))

        # Actualizamos el resumen
        self.lbl_summary.setText(f"RAM Libre Total: {total_free} MB   |   RAM Desperdiciada: {total_wasted} MB")