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
        # Get parameters from config if available
        params = filters_config.get('filters', {}).get('zoom_in_effect', {}).get('parameters', {})
        
        self.scale = params.get('initial_scale', scale)
        self.scale_speed = params.get('scale_speed', scale_speed)
        self.max_scale = params.get('max_scale', 3)
        self.opacity = params.get('opacity', 1.0)
        self.total_duration = params.get('total_duration', 1.0)
        self.animation_time = params.get('initial_animation_time', 0)
        self._snapshot = None

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

        return self.scale <= self.max_scale and self.opacity > 0

class ZoomInSnapshot:
    snapshots = []
    max_snapshots = 10

    # Initialize with config parameters
    @staticmethod
    def load_config():
        if 'zoom_in_effect' in filters_config.get('filters', {}):
            params = filters_config['filters']['zoom_in_effect'].get('parameters', {})
            ZoomInSnapshot.max_snapshots = params.get('max_snapshots', ZoomInSnapshot.max_snapshots)

    def __init__(self):
        # Load configuration when instantiated
        ZoomInSnapshot.load_config()

    @staticmethod
    def create_snapshot(frame):
        if len(ZoomInSnapshot.snapshots) >= ZoomInSnapshot.max_snapshots:
            ZoomInSnapshot.snapshots.pop()
        ZoomInSnapshot.snapshots.append(Snapshot())
        return ZoomInSnapshot.update(frame)

    @staticmethod
    def update(frame):
        result_frame = frame.copy()

        # Remove expired snapshots and update remaining ones
        ZoomInSnapshot.snapshots = [s for s in ZoomInSnapshot.snapshots if s.update(frame)]

        for snapshot in ZoomInSnapshot.snapshots[::-1]:
            if snapshot._snapshot is None:
                continue

            # Center the snapshot
            h, w = snapshot._snapshot.shape[:2]
            frame_h, frame_w = frame.shape[:2]
            x, y = (frame_w - w) // 2, (frame_h - h) // 2

            # Calculate valid regions
            x_start, y_start = max(0, x), max(0, y)
            x_end, y_end = min(frame_w, x + w), min(frame_h, y + h)
            snap_x_start, snap_y_start = max(0, -x), max(0, -y)
            snap_x_end = snap_x_start + (x_end - x_start)
            snap_y_end = snap_y_start + (y_end - y_start)

            # Get regions of interest
            roi = result_frame[y_start:y_end, x_start:x_end]
            snap_roi = snapshot._snapshot[snap_y_start:snap_y_end, snap_x_start:snap_x_end]

            if roi.shape == snap_roi.shape:
                if snapshot.opacity < 1.0:
                    cv2.addWeighted(snap_roi, snapshot.opacity, roi, 1.0 - snapshot.opacity, 0, roi)
                else:
                    result_frame[y_start:y_end, x_start:x_end] = snap_roi

        return result_frame
