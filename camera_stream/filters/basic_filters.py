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

def zoom_in_effect(frame):
    """
    Zoom in on the frame.
    """
    if not filters_config.get('filters', {}).get('zoom_in_effect', {}).get('enabled', True):
        return _empty(frame)

    zis = ZoomInSnapshot()
    return zis(frame)

class Snapshot:
    def __init__(self, scale=1, scale_speed=0.01):
        self.scale = scale
        self.scale_speed = scale_speed
        self._snapshot = None
        self.opacity = 0.8
        
        # Get parameters from config if available
        if 'zoom_in_effect' in filters_config.get('filters', {}):
            params = filters_config['filters']['zoom_in_effect'].get('parameters', {})
            self.scale_speed = params.get('scale_speed', scale_speed)
            self.opacity = params.get('opacity', 0.8)
            
    def update(self, frame):
        # Create a snapshot of the current frame with the current scale
        self._snapshot = cv2.resize(frame.copy(), None, fx=self.scale, fy=self.scale)
        
        # Increase scale for next update
        self.scale += self.scale_speed
        
        # Start reducing opacity when scale reaches 2.0 (2/3 of max size)
        self.opacity -= 0.05  # Gradually reduce opacity
        if self.opacity < 0:
            self.opacity = 0
        
        return self.scale <= 3.0 and self.opacity > 0

class ZoomInSnapshot:
    snapshots = []
    timer = 0
    interval = 50
    
    # Initialize with config parameters
    @classmethod
    def load_config(cls):
        if 'zoom_in_effect' in filters_config.get('filters', {}):
            params = filters_config['filters']['zoom_in_effect'].get('parameters', {})
            cls.interval = params.get('interval', 50)
    
    def __init__(self):
        # Load configuration when instantiated
        ZoomInSnapshot.load_config()
        ZoomInSnapshot.timer += 1 # Incrementing the timer is based on the frame rate not the time

    def __call__(self, frame):
        if ZoomInSnapshot.timer % ZoomInSnapshot.interval == 0:
            # Create a new snapshot and add it to the list
            self.snapshots.append(Snapshot())
        
        # Create a copy of the original frame to overlay snapshots on
        result_frame = frame.copy()
        
        # Process each snapshot
        to_remove = []
        for snapshot in self.snapshots:
            # Update the snapshot and check if it should be kept
            if not snapshot.update(frame):
                to_remove.append(snapshot)
                continue
            
            # Get the snapshot image
            snap_img = snapshot._snapshot
            if snap_img is None:
                continue
                
            # Calculate position to center the snapshot
            h, w = snap_img.shape[:2]
            frame_h, frame_w = frame.shape[:2]
            x = (frame_w - w) // 2
            y = (frame_h - h) // 2
            
            # Ensure the snapshot doesn't exceed frame boundaries
            # Calculate the valid region within the frame
            x_start = max(0, x)
            y_start = max(0, y)
            x_end = min(frame_w, x + w)
            y_end = min(frame_h, y + h)
            
            # Calculate the corresponding region in the snapshot
            snap_x_start = max(0, -x)
            snap_y_start = max(0, -y)
            snap_x_end = snap_x_start + (x_end - x_start)
            snap_y_end = snap_y_start + (y_end - y_start)
            
            # Apply opacity to the snapshot
            if snapshot.opacity < 1.0:
                # Create an alpha channel for blending
                alpha = snapshot.opacity
                beta = 1.0 - alpha
                
                # Only apply the snapshot to the valid region it covers
                roi = result_frame[y_start:y_end, x_start:x_end]
                snap_roi = snap_img[snap_y_start:snap_y_end, snap_x_start:snap_x_end]
                
                # Ensure ROIs have the same dimensions before blending
                if roi.shape == snap_roi.shape:
                    # Blend the snapshot with the original frame in the ROI
                    cv2.addWeighted(snap_roi, alpha, roi, beta, 0, roi)
            else:
                # If full opacity, just overlay the snapshot in the valid region
                result_frame[y_start:y_end, x_start:x_end] = snap_img[snap_y_start:snap_y_end, snap_x_start:snap_x_end]
        
        for snapshot in to_remove:
            if snapshot in self.snapshots:
                self.snapshots.remove(snapshot)
        
        return result_frame
