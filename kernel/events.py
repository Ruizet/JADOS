# kernel/events.py

class EventBus:
    """Implementa el patrón de diseño Observador (Pub/Sub)."""
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type: str, callback):
        """Permite que la GUI se suscriba a un evento específico."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def publish(self, event_type: str, data=None):
        """El Kernel usa esto para avisar que algo ocurrió."""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(data)