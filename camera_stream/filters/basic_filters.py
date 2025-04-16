"""
Filters logic for the virtual camera.
"""
import cv2
import numpy as np
import json
import os
from numpy.strings import islower as _islower

# Load filter configurations from JSON file
def load_filters_config():
    """
    Load filter configurations from the JSON file.
    """
    config_path = os.path.join(os.path.dirname(__file__), 'filters_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading filters config: {e}")
        return {"filters": {}}

# Load filter configurations
filters_config = load_filters_config()

def _filters():
    """
    List of available filters.
    """
    for name, obj in globals().items():
        if callable(obj) and not name.startswith("_") and _islower(name):
            if filters_config.get('filters', {}).get(name, {}).get('enabled', True):
                yield name, obj

def _get_filters_from_list(filters):
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

def _get_filter(filter_name):
    """
    Get a filter function by name.
    """
    func = globals().get(filter_name)
    if func:
        return func
    
    print(f"Filter '{filter_name}' not found.")
    return _empty

def _empty(frame):
    """
    Empty filter.
    """
    return frame

def horizontal_flip(frame):
    """
    Flip the frame horizontally.
    """
    if not filters_config.get('filters', {}).get('horizontal_flip', {}).get('enabled', True):
        return _empty(frame)

    return cv2.flip(frame, 1)

def minimize_colors(frame):
    """
    Minimize the number of colors in the frame.
    """
    if not filters_config.get('filters', {}).get('minimize_colors', {}).get('enabled', True):
        return _empty(frame)

    # Get parameters from config if available
    color_levels = 64  # Default value
    if 'minimize_colors' in filters_config.get('filters', {}):
        params = filters_config['filters']['minimize_colors'].get('parameters', {})
        color_levels = params.get('color_levels', color_levels)
    
    minimized_frame = np.floor(frame / color_levels) * color_levels
    minimized_frame = np.uint8(minimized_frame)
    return minimized_frame
