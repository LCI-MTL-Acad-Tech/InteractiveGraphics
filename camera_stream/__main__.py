from core import CameraStream
from filters import _get_filters_from_list, horizontal_flip, _filters
import argparse
import webbrowser
import time

def _test(camera_stream) -> None:
    """
    Test the camera stream.
    """
    result = camera_stream.camera.test_camera()
    if result:
        print("Camera is working.")
    else:
        print("Camera is not working. Please check the camera connection.")

def _preview(camera_stream) -> None:
    """
    Preview the camera stream.
    """
    try:
        camera_stream.camera.preview_camera()
    except ValueError as e:
        print(e)

def _stream(camera_stream, args):
    camera_stream.start_stream(host=args.host, port=args.port)
    
    # Open browser if requested
    if args.open_browser:
        url = f"http://{args.host}:{args.port}/"
        print(f"Opening browser to {url}")
        time.sleep(1)  # Give the server a moment to start
        webbrowser.open(url)
        
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping camera stream...")
        camera_stream.stop_stream()

def main() -> None:
    """
    Main function to parse arguments and run the camera stream test.
    """
    parser = argparse.ArgumentParser(description="Camera Stream Test")
    parser.add_argument("-i", "--camera_source", default="0", help="Camera source (default is 0 for the default camera)")
    parser.add_argument("-t", "--test", action="store_true", help="Test the camera stream")
    parser.add_argument("-p", "--preview", action="store_true", help="Preview the camera stream")
    parser.add_argument("-s", "--stream", action="store_true", default=True, help="Start the Flask MJPEG stream server (default is True)")
    parser.add_argument("-f", "--filters", nargs="+", help="List of filters to apply to the camera stream")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address for the stream server (default is 127.0.0.1)")
    parser.add_argument("--port", type=int, default=7277, help="Port number for the stream server (default is 7277)")
    parser.add_argument("--open-browser", action="store_true", help="Automatically open browser to view stream")
    args = parser.parse_args()

    camera_stream = CameraStream(source=(int(args.camera_source) if str.isdigit(args.camera_source) else args.camera_source))

    filters = [horizontal_flip]
    if args.filters:
        if args.filters == ['all']:
            print("Available filters:")
            for name, _ in _filters():
                print(name)
            return
        filters.extend(_get_filters_from_list(args.filters))
        camera_stream.add_filter(filters)

    if args.test:
        _test(camera_stream)
        return
    
    if args.preview:
        try:
            
            camera_stream.camera.preview_camera()
        except ValueError as e:
            print(e)
        return

    if args.stream:
        try:
            _stream(camera_stream, args)
        except Exception as e:
            print(f"Error starting stream: {e}")
            return

if __name__ == "__main__":
    main()
