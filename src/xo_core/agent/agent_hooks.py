# XO Agent Hooks - Central Event Dispatcher


class AgentHooks:
    def __init__(self):
        self.handlers = {}

    def register(self, event_name, handler_func):
        self.handlers[event_name] = handler_func

    def dispatch(self, event_name, payload):
        if event_name in self.handlers:
            return handler_func(payload)
        return {"error": f"Unknown event: {event_name}"}


__all__ = ["AgentHooks"]
