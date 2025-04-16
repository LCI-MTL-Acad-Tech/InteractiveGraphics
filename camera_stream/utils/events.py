class EventsManager:
    events = []

    def add_event(self, event):
        EventsManager.events.append(event)

    def remove_event(self, event):
        EventsManager.events.remove(event)

    def clear_events(self):
        EventsManager.events.clear()

    def get_events(self):
        return EventsManager.events

class Event:
    CLICK_EVENT = "click"
    KEY_EVENT = "key"
    MOUSE_EVENT = "mouse"
    UNKNOWN_EVENT = "unknown"

    def __init__(self, name, data):
        self.name = name
        if name not in [Event.CLICK_EVENT, Event.KEY_EVENT, Event.MOUSE_EVENT]:
            self.name = Event.UNKNOWN_EVENT
        self.data = data
