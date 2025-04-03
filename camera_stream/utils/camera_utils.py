"""
Utility functions for camera operations.
"""
import cv2
import sys
import platform
import subprocess
import numpy as np
from typing import List, Dict, Any, Optional


def check_macos_camera_permission() -> bool:
    """
    Check if the application has camera permissions on macOS.
    
    Returns:
        bool: True if permission is granted, False otherwise
    """
    if platform.system() != "Darwin":
        return True  # Not macOS, so no specific permission check needed
    
    try:
        # Use tccutil to check camera permission status
        result = subprocess.run(
            ['tccutil', 'status', 'Camera'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return "granted" in result.stdout.lower()
    except Exception:
        # If the check fails, assume we don't have permission
        return False


def request_macos_camera_permission() -> bool:
    """
    Request camera permission on macOS by showing a short-lived preview.
    
    This function will open a camera briefly to trigger the permission dialog,
    then close it immediately.
    
    Returns:
        bool: True if permission seems to be granted, False otherwise
    """
    if platform.system() != "Darwin":
        return True  # Not macOS, so no permission request needed
    
    try:
        # Create a window that will be shown very briefly
        cv2.namedWindow('Camera Permission Request', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Camera Permission Request', 640, 480)
        
        # Display a message
        blank_image = 255 * np.ones((480, 640, 3), np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(blank_image, 'Requesting Camera Permission...', (100, 240), font, 0.8, (0, 0, 0), 2)
        cv2.imshow('Camera Permission Request', blank_image)
        cv2.waitKey(500)  # Show message for half a second
        
        # Try to open camera 0 briefly to trigger permission dialog
        cap = cv2.VideoCapture(0)
        success = cap.isOpened()
        if success:
            # Read a single frame to ensure permission is triggered
            ret, _ = cap.read()
            success = ret
            cap.release()
        
        # Close the window
        cv2.destroyWindow('Camera Permission Request')
        return success
    except Exception:
        return False


def list_macos_cameras() -> List[int]:
    """
    List available cameras on macOS without opening them (when possible).
    
    Returns:
        List of available camera indices
    """
    try:
        # Use system_profiler to get camera information without requiring permissions
        result = subprocess.run(
            ['system_profiler', 'SPCameraDataType'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        cameras = []
        if "Camera" in result.stdout:
            # At least one camera exists, add camera index 0
            cameras.append(0)
            
            # Count additional cameras based on the output
            # This is an approximation as system_profiler doesn't provide indices
            camera_count = result.stdout.count("Camera:")
            for i in range(1, camera_count):
                cameras.append(i)
        
        return cameras
    except Exception:
        # Fall back to the regular method if the system_profiler approach fails
        return []


def list_available_cameras(max_cameras: int = 10) -> List[int]:
    """
    Lists available camera devices.
    
    On macOS, tries to use system methods to list cameras without opening them.
    Falls back to the traditional method of trying to open each camera.
    
    Args:
        max_cameras: Maximum number of cameras to check
        
    Returns:
        List of available camera indices
    """
    # For macOS, try the non-invasive method first
    if platform.system() == "Darwin":
        macos_cameras = list_macos_cameras()
        if macos_cameras:
            return macos_cameras
    
    # Fall back to the traditional method for other platforms or if macOS method failed
    available_cameras = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras


def get_camera_properties(camera_id: int) -> Dict[str, Any]:
    """
    Get the properties of a camera device.
    
    Args:
        camera_id: Index of the camera
        
    Returns:
        Dictionary containing camera properties like resolution, FPS, etc.
    """
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open camera {camera_id}")
    
    properties = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'backend': cap.getBackendName(),
        'format': int(cap.get(cv2.CAP_PROP_FORMAT)),
        'brightness': cap.get(cv2.CAP_PROP_BRIGHTNESS),
        'contrast': cap.get(cv2.CAP_PROP_CONTRAST),
        'saturation': cap.get(cv2.CAP_PROP_SATURATION),
        'hue': cap.get(cv2.CAP_PROP_HUE),
        'gain': cap.get(cv2.CAP_PROP_GAIN),
        'exposure': cap.get(cv2.CAP_PROP_EXPOSURE)
    }
    
    cap.release()
    return properties