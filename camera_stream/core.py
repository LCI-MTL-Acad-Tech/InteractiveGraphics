"""
Core functionality of the camera streaming module.
"""
import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import threading
import time

class CameraStream:
    def __init__(self, camera_source=0):
        """
        Initialize the camera stream with the given source.

        :param camera_source: Camera source (default is 0 for the default camera).
        """
        self.camera_source = camera_source
        self.virtual_cam = None
        self.cap = None
        self.running = False
        self.thread = None
        self.frame_hooks = [] # List to hold frame processing hooks

    def test_camera(self):
        """
        Test if the camera is working by capturing a single frame.

        :return: True if the camera is working, False otherwise.
        """
        cap = cv2.VideoCapture(self.camera_source)
        if not cap.isOpened():
            return False
        ret, _ = cap.read()
        cap.release()
        return ret
    
    def preview_camera(self):
        """
        Preview the camera stream in a window.
        """
        cap = cv2.VideoCapture(self.camera_source)
        if not cap.isOpened():
            raise ValueError(f"Camera source {self.camera_source} is not available.")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
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

    def start_stream(self):
        """
        Start the camera stream.

        :return: Camera object.
        """
        if self.running:
            raise RuntimeError("Camera stream is already running.")

        self.cap = cv2.VideoCapture(self.camera_source)

        if not self.cap.isOpened():
            raise ValueError(f"Camera source {self.camera_source} is not available.")

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        self.virtual_cam = pyvirtualcam.Camera(width=width, 
                                          height=height, 
                                          fps=fps,
                                          device='CS Virtual Camera')
        print(f"Using virtual camera: {self.virtual_cam.device}")

        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        """
        Update the camera stream in a separate thread.
        """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            for hook in self.frame_hooks:
                frame = hook(frame)

            self.virtual_cam.send(frame)
            self.virtual_cam.sleep_until_next_frame()

    def stop_stream(self):
        """
        Stop the camera stream.
        """
        if not self.running:
            raise RuntimeError("Camera stream is not running.")

        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        if self.virtual_cam:
            self.virtual_cam.close()
