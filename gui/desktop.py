# gui/desktop.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QMessageBox, QMdiArea)
from PySide6.QtCore import QTimer, QTime
from gui.file_manager import FileManager
from gui.task_manager import TaskManager
from gui.terminal import Terminal
from gui.memory_window import MemoryWindow

class Desktop(QMainWindow):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel  # Guardamos la referencia al Kernel
        self.setWindowTitle("JustinOS")
        self.resize(1024, 768)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.workspace = QMdiArea()
        self.workspace.setStyleSheet("background-color: #2c3e50;")
        layout.addWidget(self.workspace)

        self._init_taskbar(layout)
        self._init_desktop_icons()
        
        # Timer global del sistema operativo (Tick del Kernel)
        self.os_timer = QTimer(self)
        self.os_timer.timeout.connect(self._system_tick)
        self.os_timer.start(1000) # 1 tick por segundo

    def _init_taskbar(self, parent_layout):
        self.taskbar = QWidget()
        self.taskbar.setStyleSheet("background-color: #1a252f; color: white;")
        self.taskbar.setFixedHeight(40)
        
        tb_layout = QHBoxLayout(self.taskbar)
        tb_layout.setContentsMargins(10, 5, 10, 5)

        self.btn_start = QPushButton("Inicio")
        self.btn_start.setStyleSheet("background-color: #e74c3c; font-weight: bold; padding: 5px 15px;")
        self.btn_start.clicked.connect(self._show_start_menu_placeholder)
        tb_layout.addWidget(self.btn_start)

        tb_layout.addStretch()

        self.lbl_status = QLabel("Estado: Apagado")
        self.lbl_status.setStyleSheet("padding-right: 20px;")
        tb_layout.addWidget(self.lbl_status)

        self.lbl_clock = QLabel()
        tb_layout.addWidget(self.lbl_clock)
        
        # El reloj visual de la barra de tareas sigue siendo de la UI
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self._update_clock)
        self.ui_timer.start(1000)
        self._update_clock()

        parent_layout.addWidget(self.taskbar)

    def _init_desktop_icons(self):
        icon_container = QWidget(self.workspace)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(15, 15, 15, 15)
        icon_layout.setSpacing(15)
        
        btn_files = QPushButton("📁 Archivos")
        btn_tasks = QPushButton("⚙ Administrador")
        btn_term = QPushButton("_ Terminal")
        btn_mem = QPushButton("💾 Memoria")

        btn_style = """
            QPushButton { color: white; background: rgba(0,0,0,50); border: 1px solid rgba(255,255,255,50); 
                          border-radius: 5px; text-align: left; padding: 10px; font-size: 14px; }
            QPushButton:hover { background: rgba(255,255,255,30); }
        """
        for btn in [btn_files, btn_tasks, btn_term, btn_mem]:
            btn.setStyleSheet(btn_style)
            icon_layout.addWidget(btn)
            
        icon_layout.addStretch()
        icon_container.resize(160, 300)
        icon_container.move(10, 10)

        btn_files.clicked.connect(self.open_file_manager)
        btn_tasks.clicked.connect(self.open_task_manager)
        btn_term.clicked.connect(self.open_terminal)
        btn_mem.clicked.connect(self.open_memory_window)


    def _system_tick(self):
        """Envía un tick al Kernel y actualiza la UI."""
        self.kernel.tick()
        if self.kernel.is_running:
            self.lbl_status.setText(f"Estado: Ejecutándose | Reloj OS: {self.kernel.system_clock}")
        else:
            self.lbl_status.setText("Estado: Sistema Apagado")

    def _update_clock(self):
        self.lbl_clock.setText(QTime.currentTime().toString("hh:mm:ss"))

    def _show_start_menu_placeholder(self):
        QMessageBox.information(self, "Menú de Inicio", "[PLACEHOLDER]\nEl menú de aplicaciones se listará aquí.")

    # En gui/desktop.py, modifica este método:
    def open_file_manager(self):
        win = FileManager(self.kernel) # <-- Le pasamos el Kernel
        sub = self.workspace.addSubWindow(win)
        sub.resize(400, 300)
        sub.show()

    def open_task_manager(self):
        win = TaskManager(self.kernel) # <-- Le pasamos el Kernel
        sub = self.workspace.addSubWindow(win)
        sub.resize(550, 300)
        sub.show()

    def open_terminal(self):
        win = Terminal(self.kernel) # Le pasamos el Kernel a la Terminal
        sub = self.workspace.addSubWindow(win)
        sub.resize(500, 350)
        sub.show()

    def open_memory_window(self):
        win = MemoryWindow(self.kernel)
        sub = self.workspace.addSubWindow(win)
        sub.resize(650, 350)
        sub.show()