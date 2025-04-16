"""
Filters logic for the virtual camera.
"""
from .config import _get_filter, _get_filters_from_list, _filters

from .basic_filters import horizontal_flip, minimize_colors

from .zoom_in_snapshots import zoom_in_effect

from .events import EventsManager, Event

__all__ = [
    "_get_filter",
    "_get_filters_from_list",
    "_filters",
    "horizontal_flip",
    "minimize_colors",
    "zoom_in_effect",
    "Event",
    "EventsManager"
]