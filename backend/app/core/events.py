# ============================================================
# Core — Events
# ============================================================

from typing import Callable, Dict, List, Any
import asyncio

class EventDispatcher:
    """
    Simple asynchronous event dispatcher to decouple modules.
    Used for dispatching events like leaf completions to the Streak/XP engines.
    """

    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event_name: str, callback: Callable[..., Any]):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[..., Any]):
        if event_name in self._listeners and callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)

    async def emit(self, event_name: str, *args, **kwargs):
        """Emit an event asynchronously to all subscribed listeners."""
        if event_name in self._listeners:
            callbacks = self._listeners[event_name]
            tasks = [cb(*args, **kwargs) for cb in callbacks]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

# Instantiate a global dispatcher
events = EventDispatcher()

