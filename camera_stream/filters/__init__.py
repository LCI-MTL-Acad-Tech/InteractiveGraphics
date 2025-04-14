"""
Filters logic for the virtual camera.
"""

from .basic_filters import horizontal_flip, \
    get_filter, \
    get_filters_from_list, \
    minimize_colors

__all__ = [
    "horizontal_flip",
    "get_filter",
    "get_filters_from_list",
    "minimize_colors",
]