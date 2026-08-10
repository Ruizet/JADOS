# gui/file_manager.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from filesystem.directory import Directory

class FileManager(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.setWindowTitle("Explorador de Archivos Virtual")
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Sistema de Archivos Virtual (Sincronizado)")
        layout.addWidget(self.tree)

        # FASE 9: Adiós al botón manual. Hola programación orientada a eventos.
        if self.kernel:
            self.kernel.events.subscribe("FS_CHANGED", self._load_real_data)
            self._load_real_data()

    def _load_real_data(self, data=None):
        self.tree.clear()
        if not self.kernel or not self.kernel.fs:
            return

        root_node = self.kernel.fs.root
        root_item = QTreeWidgetItem(self.tree, [f"📁 {root_node.name} (raíz)"])
        self._populate_tree(root_node, root_item)
        self.tree.expandAll()

    def _populate_tree(self, directory: Directory, parent_item: QTreeWidgetItem):
        for elem in directory.list_elements():
            if isinstance(elem, Directory):
                item = QTreeWidgetItem(parent_item, [f"📁 {elem.name}"])
                self._populate_tree(elem, item)
            else:
                QTreeWidgetItem(parent_item, [f"📄 {elem.name} ({elem.size} B)"])