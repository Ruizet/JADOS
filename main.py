# main.py
import sys
from PySide6.QtWidgets import QApplication
from gui.desktop import Desktop
from kernel.kernel import Kernel

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 1. Inicializar el Core (Kernel)
    kernel = Kernel()
    
    # 2. Inicializar la GUI pasándole el Kernel
    desktop = Desktop(kernel)
    desktop.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()