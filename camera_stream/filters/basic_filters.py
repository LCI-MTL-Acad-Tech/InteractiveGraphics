"""
Filters logic for the virtual camera.
"""
import cv2

def horizontal_flip(frame):
    """
    Flip the frame horizontally.
    """
    return cv2.flip(frame, 1)