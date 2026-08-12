from collections import deque

from app.models.event import PlatformEvent


class EventRepository:
    def __init__(self, max_events: int = 1000):
        self._events = deque(
            maxlen=max_events
        )

    def add(
        self,
        event: PlatformEvent
    ) -> PlatformEvent:
        self._events.append(event)
        return event

    def list(
        self
    ) -> list[PlatformEvent]:
        return list(self._events)


event_repository = EventRepository()
