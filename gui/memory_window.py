# gui/memory_window.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from PySide6.QtCore import Qt
from gui.bitmap_widget import BitmapWidget
from gui.linked_list_widget import LinkedListWidget
from gui.buddy_widget import BuddyWidget
from gui.virtual_memory_widget import VirtualMemoryWidget

class MemoryWindow(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.setWindowTitle("Admon. Memoria")
        self.resize(900, 600)

        main_layout = QVBoxLayout(self)

        self.main_tabs = QTabWidget()
        main_layout.addWidget(self.main_tabs)

        # Pestaña A: Asignación Dinámica
        self.tab_dynamic = QWidget()
        self._init_dynamic_tab()
        self.main_tabs.addTab(self.tab_dynamic, "Asignación dinámica")

        # Pestaña B: Memoria Virtual
        self.tab_virtual = QWidget()
        self._init_virtual_tab()
        self.main_tabs.addTab(self.tab_virtual, "Memoria virtual")

    def _init_dynamic_tab(self):
        layout = QVBoxLayout(self.tab_dynamic)
        
        # Aquí es donde se crea la variable que te daba error
        self.dynamic_subtabs = QTabWidget()
        layout.addWidget(self.dynamic_subtabs)

        # 1. Mapa de Bits (Vista real cargada)
        self.sub_bitmap = BitmapWidget(self.kernel)
        self.dynamic_subtabs.addTab(self.sub_bitmap, "Mapa de bits")

        # 2. Listas Ligadas (Placeholder para la Fase 6)
        self.sub_linked = LinkedListWidget(self.kernel)
        self.dynamic_subtabs.addTab(self.sub_linked, "Listas ligadas")

        # 3. Buddy System (Placeholder para la Fase 7)
        self.sub_buddy = BuddyWidget(self.kernel)
        self.dynamic_subtabs.addTab(self.sub_buddy, "Sistema de asociados / Buddy System")        

    def _init_virtual_tab(self):
        layout = QVBoxLayout(self.tab_virtual)
        layout.setContentsMargins(0, 0, 0, 0) # Para que ocupe todo el espacio
        
        self.sub_virtual = VirtualMemoryWidget(self.kernel)
        layout.addWidget(self.sub_virtual)