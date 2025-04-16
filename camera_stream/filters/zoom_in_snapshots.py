import cv2
from .events import EventsManager
from .config import filters_config, register_filter

def _empty(frame):
    """
    Empty filter.
    """
    return frame

def zoom_in_effect(frame):
    """
    Zoom in on the frame.
    """
    if not filters_config.get('filters', {}).get('zoom_in_effect', {}).get('enabled', True):
        return _empty(frame)
    
    config_key = filters_config.get('filters', {}).get('zoom_in_effect', {}).get('parameters', {}).get('key', 'space')

    if EventsManager.get_key_pressed(config_key):
        return ZoomInSnapshot.create_snapshot(frame)
    
    return ZoomInSnapshot.update(frame)

# Register the filter
register_filter('zoom_in_effect', zoom_in_effect)
class Snapshot:
    def __init__(self, scale=1, scale_speed=0.01):
        self.scale = scale
        self.scale_speed = scale_speed
        self.max_scale = 3
        self._snapshot = None
        self.opacity = 1.0
        self.animation_time = 0
        self.total_duration = 1.0
        
        # Get parameters from config if available
        if 'zoom_in_effect' in filters_config.get('filters', {}):
            params = filters_config['filters']['zoom_in_effect'].get('parameters', {})
            self.scale_speed = params.get('scale_speed', scale_speed)
            self.total_duration = params.get('total_duration', 1.0)
            self.max_scale = params.get('max_scale', self.max_scale)
            self.opacity = params.get('opacity', self.opacity)
            
    def update(self, frame):
        # Create a snapshot of the current frame with the current scale
        self._snapshot = cv2.resize(frame.copy(), None, fx=self.scale, fy=self.scale)
        
        # Calculate progress (0 to 1) based on animation time
        progress = min(self.animation_time / self.total_duration, 1.0)
        
        # Update scale and opacity based on animation progress
        self.scale = 1 + (2 * progress)  # Scale from 1 to 3
        self.opacity = max(0, 1 - progress)  # Opacity from 1 to 0
        
        # Increment animation time
        self.animation_time += self.scale_speed
        
        return self.scale <= 3.0 and self.opacity > 0

class ZoomInSnapshot:
    snapshots = []
    max_snapshots = 10

    # Initialize with config parameters
    def load_config():
        if 'zoom_in_effect' in filters_config.get('filters', {}):
            params = filters_config['filters']['zoom_in_effect'].get('parameters', {})
            ZoomInSnapshot.max_snapshots = params.get('max_snapshots', ZoomInSnapshot.max_snapshots)

    def __init__(self):
        # Load configuration when instantiated
        ZoomInSnapshot.load_config()

    def create_snapshot(frame):
        ZoomInSnapshot.snapshots.append(Snapshot())
        return ZoomInSnapshot.update(frame)
    
    def update(frame):
        # Create a copy of the original frame to overlay snapshots on
        result_frame = frame.copy()
        
        # Process each snapshot
        to_remove = []
        for snapshot in ZoomInSnapshot.snapshots:
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
            if snapshot in ZoomInSnapshot.snapshots:
                ZoomInSnapshot.snapshots.remove(snapshot)
        
        return result_frame
