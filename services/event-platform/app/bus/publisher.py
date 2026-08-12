from app.models.event import PlatformEvent


class InMemoryEventPublisher:
    def __init__(self):
        self.events: list[PlatformEvent] = []

    def publish(self, event: PlatformEvent) -> PlatformEvent:
        self.events.append(event)
        return event

    def list_events(self) -> list[PlatformEvent]:
        return list(self.events)


publisher = InMemoryEventPublisher()
