# filesystem/file.py

class File:
    def __init__(self, name: str, content: str = ""):
        self.name = name
        self.content = content
        self.size = len(content)

    def to_dict(self):
        return {
            "type": "file",
            "name": self.name,
            "content": self.content,
            "size": self.size
        }

    @staticmethod
    def from_dict(data):
        return File(data["name"], data.get("content", ""))