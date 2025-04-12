"""
Core functionality of the camera streaming module.
"""
from utils import Camera
import cv2
import threading
from flask import Flask, Response, render_template
import time
import os
import sys

class CameraStream:
    def __init__(self, source=0):
        """
        Initialize the camera stream with the given source

        :param source: Camera source (default is 0 for the default camera).
        """
        self.camera = Camera(source)
        self.running = False
        self.app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
        self.server_thread = None

        # Register Flask routes
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self._generate_frames(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

    def _generate_frames(self):
        """
        Generator function that yields frames for the MJPEG stream.
        """
        if not self.running:
            return

        while self.running:
            try:
                frame = self.camera._update()
                _, buffer = cv2.imencode('.jpg', frame)
                frame_data = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                time.sleep(0.01)  # Small delay to control frame rate
            except Exception as e:
                print(f"Error generating frame: {e}")
                break

    def start_stream(self, host="127.0.0.1", port=7277):
        """
        Start the Flask server to stream camera frames

        :param host: Host address to bind the server (default is "127.0.0.1")
        :param port: Port number to bind the server (default is 7277)
        """
        if self.running:
            raise RuntimeError("Camera stream is already running.")

        self.camera.cap = cv2.VideoCapture(self.camera.source)

        if not self.camera.cap.isOpened():
            raise ValueError(f"Camera source {self.camera.source} is not available.")

        self.running = True

        # Start Flask server in a separate thread
        def run_server():
            self.app.run(host=host, port=port, debug=False, threaded=True)

        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        print(f"Camera stream server started at http://{host}:{port}/")

    def stop_stream(self):
        """
        Stop the camera stream and Flask server.
        """
        if not self.running:
            raise RuntimeError("Camera stream is not running.")

        self.running = False

        # Clean up resources
        if self.camera.cap and self.camera.cap.isOpened():
            self.camera.cap.release()

        cv2.destroyAllWindows()
        print("Camera stream server stopped.")
