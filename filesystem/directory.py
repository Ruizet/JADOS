# filesystem/directory.py
from filesystem.file import File

class Directory:
    def __init__(self, name: str):
        self.name = name
        self.children = {}  # nombre -> File o Directory

    def add_element(self, element):
        self.children[element.name] = element

    def remove_element(self, name: str) -> bool:
        if name in self.children:
            del self.children[name]
            return True
        return False

    def get_element(self, name: str):
        return self.children.get(name)

    def list_elements(self) -> list:
        return list(self.children.values())

    def to_dict(self):
        return {
            "type": "directory",
            "name": self.name,
            "children": {k: v.to_dict() for k, v in self.children.items()}
        }

    @staticmethod
    def from_dict(data):
        d = Directory(data["name"])
        for child_data in data.get("children", {}).values():
            if child_data.get("type") == "directory":
                d.add_element(Directory.from_dict(child_data))
            else:
                d.add_element(File.from_dict(child_data))
        return d