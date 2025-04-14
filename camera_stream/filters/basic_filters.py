"""
Filters logic for the virtual camera.
"""
import cv2
import numpy as np

def get_filters_from_list(filters):
    """
    Apply filters based on the command-line arguments.
    """
    _filters = []

    for filter_name in filters:
        func = globals().get(filter_name)
        if func: 
            _filters.append(func)
        else:
            print(f"Filter '{filter_name}' not found. Skipping...")

    return _filters

def get_filter(filter_name):
    """
    Get a filter function by name.
    """
    func = globals().get(filter_name)
    if func:
        return func
    return None

def horizontal_flip(frame):
    """
    Flip the frame horizontally.
    """
    return cv2.flip(frame, 1)

def minimize_colors(frame):
    """
    Minimize the number of colors in the frame.
    """
    minimized_frame = np.floor(frame / 64) * 64
    minimized_frame = np.uint8(minimized_frame)
    return minimized_frame
