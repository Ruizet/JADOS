# gui/terminal.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QCompleter
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

class TerminalInput(QLineEdit):
    """Clase personalizada para manejar el historial de comandos con las flechas."""
    def __init__(self):
        super().__init__()
        self.history = []
        self.history_index = -1

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.history and self.history_index > 0:
                self.history_index -= 1
                self.setText(self.history[self.history_index])
        elif event.key() == Qt.Key_Down:
            if self.history and self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.setText(self.history[self.history_index])
            elif self.history_index == len(self.history) - 1:
                self.history_index += 1
                self.clear()
        else:
            super().keyPressEvent(event)

    def add_to_history(self, command: str):
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_index = len(self.history)


class Terminal(QWidget):
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.setWindowTitle("Terminal MiniOS")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Área de salida (solo lectura, soporta HTML)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas, monospace; font-size: 14px;")
        layout.addWidget(self.output)

        # Área de entrada personalizada con historial
        self.input = TerminalInput()
        self.input.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: Consolas, monospace; font-size: 14px; border: 1px solid #333;")
        self.input.returnPressed.connect(self.process_command)
        layout.addWidget(self.input)

        # --- Autocompletado (TAB) ---
        self.commands_list = ["boot", "shutdown", "run", "ps", "kill", "mem", "ls", "cd", "mkdir", "touch", "cat", "rm", "help", "clear", "about"]
        completer = QCompleter(self.commands_list, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.input.setCompleter(completer)

        self.prompt = "<span style='color: #f39c12;'>MiniOS&gt;</span> "
        self._print_html("<span style='color: #00ff00; font-weight: bold;'>MiniOS Terminal v3.0 (UX Upgraded)</span>")
        self._print_html("<span style='color: #888888;'>Escriba 'boot' para iniciar el sistema o 'help' para ayuda.</span><br>")

    def _print_html(self, html_text: str):
        """Imprime texto interpretando HTML y hace auto-scroll al final."""
        self.output.append(html_text)
        # Mueve el cursor al final para hacer scroll automático
        self.output.moveCursor(QTextCursor.End)

    def _format_response(self, text: str) -> str:
        """Aplica colores dependiendo del contenido de la respuesta."""
        # Convertimos saltos de línea a etiquetas <br> para HTML
        text = text.replace("\n", "<br>").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
        
        if text.startswith("Error:"):
            return f"<span style='color: #ff5555; font-weight: bold;'>{text}</span>"
        elif text.startswith("[Kernel]"):
            return f"<span style='color: #55ffff;'>{text}</span>"
        else:
            return f"<span style='color: #00ff00;'>{text}</span>"

    def process_command(self):
        cmd_line = self.input.text().strip()
        self.input.clear()
        if not cmd_line:
            return

        # 1. Guardar en historial
        self.input.add_to_history(cmd_line)

        # 2. Imprimir el prompt con el comando que introdujo el usuario
        self._print_html(f"{self.prompt}<span style='color: #ffffff;'>{cmd_line}</span>")
        
        parts = cmd_line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        # 3. Procesar comandos
        if cmd == "help":
            help_text = (
                "<span style='color: #aaddff;'>"
                "<b>Comandos del Sistema:</b><br>"
                "  boot, shutdown<br>"
                "<b>Procesos y Memoria:</b><br>"
                "  run &lt;nombre&gt; [mem] [tiempo], ps, kill &lt;pid&gt;, mem<br>"
                "<b>Sistema de Archivos:</b><br>"
                "  ls, cd &lt;dir&gt;, mkdir &lt;dir&gt;, touch &lt;archivo&gt;, cat &lt;archivo&gt;, rm &lt;elemento&gt;<br>"
                "<b>Terminal:</b><br>"
                "  clear, about, help"
                "</span>"
            )
            self._print_html(help_text)
        elif cmd == "clear":
            self.output.clear()
        elif cmd == "about":
            self._print_html("<span style='color: #ffff55;'>MiniOS - FASE 8 (Terminal Enriquecida)</span>")
        else:
            # Enviar al Kernel y formatear la respuesta
            raw_response = self.kernel.execute_command(cmd, args)
            formatted_response = self._format_response(raw_response)
            self._print_html(formatted_response)