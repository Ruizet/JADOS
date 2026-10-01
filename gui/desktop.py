# gui/desktop.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QMdiArea, QLabel)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap
from pathlib import Path

# Importaciones de las aplicaciones
from gui.terminal import Terminal
from gui.file_manager import FileManager
from gui.task_manager import TaskManager
from gui.memory_window import MemoryWindow

class Desktop(QMainWindow):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.setWindowTitle("JADOS")
        
        # Maximizar ventana al inicio
        self.setWindowState(Qt.WindowMaximized)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Área de trabajo clásica con fondo sólido
        self.workspace = QMdiArea()
        self.workspace.setStyleSheet("background-color: #2c3e50;") 
        main_layout.addWidget(self.workspace)

        self._init_taskbar()
        main_layout.addWidget(self.taskbar)

        # Reloj del sistema
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._system_tick)
        self.timer.start(1000)
        
        # Sincronización con el Kernel
        self.kernel.events.subscribe("SYSTEM_TICK", self._update_status_ui)

    def _system_tick(self):
        """Impulsa el tiempo central del Kernel."""
        self.kernel.tick()
        self._update_status_ui()

    def _update_status_ui(self, data=None):
        """Actualiza el texto de la barra inferior con el estado del SO."""
        if self.kernel.is_running:
            self.lbl_status.setText(f"🟢 Ejecutando  |  Reloj OS: {self.kernel.system_clock} t")
        else:
            self.lbl_status.setText("🔴 Apagado (Usa 'boot' en Terminal)")

    def _init_taskbar(self):
        self.taskbar = QWidget()
        self.taskbar.setFixedHeight(50)
        self.taskbar.setStyleSheet("background-color: #1a252f; border-top: 2px solid #000000;")
        
        layout = QHBoxLayout(self.taskbar)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(15)

        btn_style = """
            QPushButton { color: white; background: #34495e; border-radius: 5px; padding: 8px 15px; font-size: 14px; font-weight: bold; border: 1px solid #2c3e50; }
            QPushButton:hover { background: #415b76; border: 1px solid #5dade2; }
            QPushButton:pressed { background: #2c3e50; }
        """

        btn_files = QPushButton("📁 Archivos")
        btn_tasks = QPushButton("⚙ Administrador")
        btn_term = QPushButton("💻 Terminal")
        btn_mem = QPushButton("💾 Memoria")

        for btn in [btn_files, btn_tasks, btn_term, btn_mem]:
            btn.setStyleSheet(btn_style)
            layout.addWidget(btn)
            
        layout.addStretch()

        self.lbl_status = QLabel("🔴 Apagado (Usa 'boot' en Terminal)")
        self.lbl_status.setStyleSheet("color: white; font-weight: bold; font-size: 14px; padding-right: 15px;")
        layout.addWidget(self.lbl_status)

        # Conexiones a las apps
        btn_files.clicked.connect(self.open_file_manager)
        btn_tasks.clicked.connect(self.open_task_manager)
        btn_term.clicked.connect(self.open_terminal)
        btn_mem.clicked.connect(self.open_memory_window)

    def _center_sub_window(self, sub_window):
        self.workspace.update() 
        sub_window.adjustSize() 
        
        x = (self.workspace.width() - sub_window.width()) // 2
        y = (self.workspace.height() - sub_window.height()) // 2
        
        sub_window.move(max(0, x), max(0, y))

    def open_file_manager(self):
        win = FileManager(self.kernel)
        sub = self.workspace.addSubWindow(win)
        sub.resize(600, 400)
        self._center_sub_window(sub)
        sub.show()

    def open_task_manager(self):
        win = TaskManager(self.kernel)
        sub = self.workspace.addSubWindow(win)
        sub.resize(600, 400)
        self._center_sub_window(sub)
        sub.show()

    def open_terminal(self):
        win = Terminal(self.kernel)
        sub = self.workspace.addSubWindow(win)
        sub.resize(700, 450)
        self._center_sub_window(sub)
        sub.show()

    def open_memory_window(self):
        win = MemoryWindow(self.kernel)
        sub = self.workspace.addSubWindow(win)
        sub.resize(900, 600)
        self._center_sub_window(sub)
        sub.show()