"""
Utility functions for camera operations.
"""

import cv2
import time
import socket
import struct
import numpy as np

class Camera:
    def __init__(self, source=0):
        """
        Initialize the camera with the given source.

        :param source: Camera source (default is 0 for the default camera).
        """
        self.source = source
        self.cap = None
        self.frame_hooks = [] # List to hold frame processing hooks

    def test_camera(self):
        """
        Test if the camera is working by capturing a single frame.

        :return: True if the camera is working, False otherwise.
        """
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            return False
        ret, _ = cap.read()
        cap.release()
        return ret

    def preview_camera(self):
        """
        Preview the camera stream in a window.
        """
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            raise ValueError(f"Camera source {self.source} is not available.")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    input("Failed to read frame from camera. Press Enter to continue...")
                    break

                for hook in self.frame_hooks:
                    frame = hook(frame)

                cv2.imshow("Camera Preview", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            print("Preview interrupted by user.")
        finally:
            if cap.isOpened():
                cap.release()
            cv2.destroyAllWindows()
            print("Camera preview closed.")

    def add_frame_hook(self, hook):
        """
        Add a hook function to process frames.

        :param hook: Function to process frames.
        """
        self.frame_hooks.append(hook)

    def _update(self):
        """
        Update the camera stream.

        :return: Returns the frame
        """
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame from camera.")

        for hook in self.frame_hooks:
            frame = hook(frame)

        return frame
