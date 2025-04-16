from numpy.strings import islower as _islower
import os
import json
import importlib
import sys

# Load filter configurations from JSON file
def _load_filters_config():
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

filters_config = _load_filters_config()
_filter_registry = {}

def register_filter(name, filter_func):
    """
    Register a filter function.
    """
    _filter_registry[name] = filter_func

def _filters():
    """
    List of available filters.
    """
    for name, func in _filter_registry.items():
        if filters_config.get('filters', {}).get(name, {}).get('enabled', True):
            yield name, func

def _get_filters_from_list(filters):
    """
    Apply filters based on the command-line arguments.
    """
    _filters = []

    for filter_name in filters:
        func = _filter_registry.get(filter_name)
        if func: 
            _filters.append(func)
        else:
            print(f"Filter '{filter_name}' not found. Skipping...")

    return _filters

def _get_filter(filter_name):
    """
    Get a filter function by name.
    """
    func = _filter_registry.get(filter_name)
    if func:
        return func
    
    print(f"Filter '{filter_name}' not found.")
    return _empty

def _empty(frame):
    """
    Empty filter.
    """
    return frame
