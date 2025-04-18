"""
Filters logic for the virtual camera.
"""

import cv2
import numpy as np
from .config import filters_config, register_filter


def horizontal_flip(frame):
    """
    Flip the frame horizontally.
    """
    if (
        not filters_config.get("filters", {})
        .get("horizontal_flip", {})
        .get("enabled", True)
    ):
        return _empty(frame)

    return cv2.flip(frame, 1)


def minimize_colors(frame):
    """
    Minimize the number of colors in the frame.
    """
    if (
        not filters_config.get("filters", {})
        .get("minimize_colors", {})
        .get("enabled", True)
    ):
        return _empty(frame)

    color_levels = 64
    if "minimize_colors" in filters_config.get("filters", {}):
        params = filters_config["filters"]["minimize_colors"].get("parameters", {})
        color_levels = params.get("color_levels", color_levels)

    minimized_frame = np.floor(frame / color_levels) * color_levels
    minimized_frame = np.uint8(minimized_frame)
    return minimized_frame


def triangulate_effect(frame):
    """
    Add a triangulation effect to the frame.
    """
    if (
        not filters_config.get("filters", {})
        .get("triangulate_effect", {})
        .get("enabled", True)
    ):
        return _empty(frame)

    triangulation_level = 1
    if "triangulate_effect" in filters_config.get("filters", {}):
        params = filters_config["filters"]["triangulate_effect"].get("parameters", {})
        triangulation_level = params.get("triangulation_level", triangulation_level)

    triangulated_frame = frame.copy()

    # TODO: Implement the triangulation effect

    return triangulated_frame


def _empty(frame):
    """
    Empty filter.
    """
    return frame


register_filter("horizontal_flip", horizontal_flip)
register_filter("minimize_colors", minimize_colors)
register_filter("triangulate_effect", triangulate_effect)
