from camera_stream import CameraStream
import argparse

def main() -> None:
    """
    Main function to parse arguments and run the camera stream test.
    """
    parser = argparse.ArgumentParser(description="Camera Stream Test")
    parser.add_argument("--camera_source", type=int, default=0, help="Camera source (default is 0 for the default camera)")
    parser.add_argument("-t", "--test", action="store_true", help="Test the camera stream")
    parser.add_argument("-p", "--preview", action="store_true", help="Preview the camera stream")
    parser.add_argument("-c", "--virtual_camera", action="store_true", default=True, help="Use virtual camera (default is True)")
    args = parser.parse_args()

    camera_stream = CameraStream(camera_source=args.camera_source)

    if args.test:
        result = camera_stream.test_camera()
        if result:
            print("Camera is working.")
        else:
            print("Camera is not working. Please check the camera connection.")
        return
    
    if args.preview:
        try:
            camera_stream.preview_camera()
        except ValueError as e:
            print(e)
        return

    if args.virtual_camera:
        camera_stream.start_stream()
        print("Virtual camera started.")
        if input("Press Enter to stop the camera stream...") == "":
            camera_stream.stop_stream()
            print("Virtual camera stopped.")

if __name__ == "__main__":
    main()
