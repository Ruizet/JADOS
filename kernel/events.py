# kernel/events.py

class EventBus:
    """Implementa el patrón de diseño Observador (Pub/Sub) con auto-limpieza."""
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
            dead_listeners = []
            
            for callback in self.listeners[event_type]:
                try:
                    callback(data)
                except RuntimeError:
                    # El objeto C++ (la ventana de la GUI) fue destruido por el usuario.
                    # Lo marcamos para eliminarlo de la lista y no volver a llamarlo.
                    dead_listeners.append(callback)
            
            # Limpiamos los oyentes zombis para que no consuman memoria
            for dead in dead_listeners:
                self.listeners[event_type].remove(dead)