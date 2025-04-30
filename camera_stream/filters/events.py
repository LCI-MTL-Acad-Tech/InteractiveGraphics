import keyboard
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
import threading
import time

class EventsManager:
    events = []
    def __init__(self):
        keyboard.hook(lambda e: self.on_action(e))
    
    def on_action(self, event):
        if event.event_type == KEY_DOWN:
            self.on_key_press(event)
        elif event.event_type == KEY_UP:
            self.on_key_release(event)

    def on_key_press(self, event):
        EventsManager.add_event(Event(Event.KEY_EVENT, event.name))

    def on_key_release(self, event):
        for _event in EventsManager.events:
            if _event.name == Event.KEY_EVENT and event.name == _event.data:
                EventsManager.remove_event(_event)

    @staticmethod
    def add_event(event):
        for _event in EventsManager.events:
            if _event.name == event.name and _event.data == event.data:
                return
        EventsManager.events.append(event)

    @staticmethod
    def remove_event(event):
        if event not in EventsManager.events:
            return
        EventsManager.events.remove(event)

    def clear_events(self):
        EventsManager.events.clear()

    def get_events(self):
        return EventsManager.events
    
    @staticmethod
    def get_key_pressed(key) -> bool:
        for event in EventsManager.events:
            if event.name == Event.KEY_EVENT and event.data == key:
                return True
        return False

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
