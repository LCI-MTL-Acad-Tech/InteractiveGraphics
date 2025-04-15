"""
Filters logic for the virtual camera.
"""

from .basic_filters import horizontal_flip, \
    _get_filter, \
    _get_filters_from_list, \
    _filters, \
    minimize_colors, \
    zoom_in_effect

__all__ = [
    "_get_filter",
    "_get_filters_from_list",
    "_filters",
    "horizontal_flip",
    "minimize_colors",
    "zoom_in_effect"
]