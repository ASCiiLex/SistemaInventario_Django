from collections import defaultdict


class EventBus:
    def __init__(self):
        self._listeners = defaultdict(list)

    def register(self, event_type: str, handler):
        self._listeners[event_type].append(handler)

    def emit(self, event_type: str, payload: dict):
        handlers = self._listeners.get(event_type, [])

        for handler in handlers:
            handler(payload)


# instancia global
event_bus = EventBus()


def emit_event(event_type: str, payload: dict):
    event_bus.emit(event_type, payload)


def register_event(event_type: str):
    def decorator(func):
        event_bus.register(event_type, func)
        return func
    return decorator