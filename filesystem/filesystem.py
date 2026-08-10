# filesystem/filesystem.py
import json
import os
from filesystem.file import File
from filesystem.directory import Directory

class FileSystem:
    def __init__(self, disk_path: str = "filesystem/virtual_disk.json"):
        self.disk_path = disk_path
        self.root = Directory("root")
        self.cwd = self.root  # Directorio actual
        self.path_stack = ["root"]
        self.load_disk()

    def get_cwd_path(self) -> str:
        return "/" + "/".join(self.path_stack[1:]) if len(self.path_stack) > 1 else "/"

    def create_file(self, name: str, content: str = "") -> str:
        if name in self.cwd.children:
            return f"Error: El elemento '{name}' ya existe."
        new_file = File(name, content)
        self.cwd.add_element(new_file)
        self.save_disk()
        return f"Archivo '{name}' creado exitosamente."

    def create_directory(self, name: str) -> str:
        if name in self.cwd.children:
            return f"Error: El elemento '{name}' ya existe."
        new_dir = Directory(name)
        self.cwd.add_element(new_dir)
        self.save_disk()
        return f"Directorio '{name}' creado exitosamente."

    def read_file(self, name: str) -> str:
        element = self.cwd.get_element(name)
        if not element:
            return f"Error: Archivo '{name}' no existe."
        if isinstance(element, Directory):
            return f"Error: '{name}' es un directorio, no un archivo."
        return element.content

    def remove_element(self, name: str) -> str:
        if self.cwd.remove_element(name):
            self.save_disk()
            return f"'{name}' eliminado exitosamente."
        return f"Error: Elemento '{name}' no encontrado."

    def list_directory(self) -> str:
        elements = self.cwd.list_elements()
        if not elements:
            return f"Directorio {self.get_cwd_path()} está vacío."
        out = f"Contenido de {self.get_cwd_path()}:\n"
        for elem in elements:
            tipo = "[DIR]" if isinstance(elem, Directory) else "[FILE]"
            out += f"  {tipo}\t{elem.name}\n"
        return out

    def change_directory(self, name: str) -> str:
        if name == "..":
            if len(self.path_stack) > 1:
                self.path_stack.pop()
                curr = self.root
                for folder in self.path_stack[1:]:
                    curr = curr.get_element(folder)
                self.cwd = curr
                return f"CWD cambiado a {self.get_cwd_path()}"
            return "Ya estás en el directorio raíz."
        
        element = self.cwd.get_element(name)
        if not element:
            return f"Error: Directorio '{name}' no existe."
        if not isinstance(element, Directory):
            return f"Error: '{name}' es un archivo, no un directorio."

        self.cwd = element
        self.path_stack.append(name)
        return f"CWD cambiado a {self.get_cwd_path()}"

    def save_disk(self):
        data = self.root.to_dict()
        os.makedirs(os.path.dirname(self.disk_path), exist_ok=True)
        with open(self.disk_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_disk(self):
        if os.path.exists(self.disk_path):
            try:
                with open(self.disk_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.root = Directory.from_dict(data)
                    self.cwd = self.root
                    self.path_stack = ["root"]
            except Exception:
                self._create_default_structure()
        else:
            self._create_default_structure()

    def _create_default_structure(self):
        self.root = Directory("root")
        self.cwd = self.root
        self.path_stack = ["root"]
        
        doc = Directory("Documentos")
        des = Directory("Descargas")
        sis = Directory("Sistema")
        txt = File("ejemplo.txt", "Hola mundo desde MiniOS!")
        
        self.root.add_element(doc)
        self.root.add_element(des)
        self.root.add_element(sis)
        self.root.add_element(txt)
        self.save_disk()