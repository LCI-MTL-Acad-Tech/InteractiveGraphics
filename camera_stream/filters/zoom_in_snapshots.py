from basic_filters import _empty, filters_config
from ..utils.events import Event, EventsManager

def zoom_in_effect(frame):
    """
    Zoom in on the frame.
    """
    if not filters_config.get('filters', {}).get('zoom_in_effect', {}).get('enabled', True):
        return _empty(frame)

    return frame

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
    max_snapshots = 10

    # Initialize with config parameters
    @classmethod
    def load_config(cls):
        if 'zoom_in_effect' in filters_config.get('filters', {}):
            params = filters_config['filters']['zoom_in_effect'].get('parameters', {})
            cls.max_snapshots = params.get('max_snapshots', cls.max_snapshots)
    
    def __init__(self):
        # Load configuration when instantiated
        ZoomInSnapshot.load_config()

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
