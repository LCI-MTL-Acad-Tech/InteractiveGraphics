# Updates to the Camera Stream Module

## 2025-04-12: Revamped for a Flask-Based MJPEG Stream Server

The camera stream module has been revamped to use a Flask-based MJPEG stream server. This change provides several benefits:

- This approach is a reliable solution to stream processed video frames over HTTP.
- It should be able to run on all platforms.
- It is easy to add filters and effects onto the stream.

### Issues:
- Unsure if this is the most efficient way to stream video frames over HTTP. There is a big delay in the stream but it's not too bad.

### Next Steps:
- Add filters and effects

---

## 2025-04-04: Initial Project Structure

The camera stream module is structured as follows:

```
camera_stream/
├── __init__.py          # Package initialization
├── core.py              # Core CameraStream class
├── filters/             # Camera filters
│   ├── __init__.py
│   └── basic_filters.py # Basic image filters
├── utils/               # Utility functions
│   ├── __init__.py
│   └── camera_utils.py  # Camera-related utilities
├── README.md            # Module documentation
└── updates.md           # This file - tracking changes
```

### Current Status:
- Basic structure for the camera streaming module is done
- Camera preview works

### Known Issues:
- Multi-threading is not functioning correctly
  - I'm getting a 'RuntimeError' because there is a [known issue with pyvirtualcam on MacOS](https://github.com/letmaik/pyvirtualcam/issues/111)
- Need to implement macOS-specific camera permissions handling
- Because of the threading issue, the functionalities of `start_stream`, `stop_stream` and `_update` are not working as expected.
- Idk if I should stream the output into a virtual camera I'm not gonna lie, maybe we'll just stream it into a web server.

### Next Steps:
- Fix the threading issue
- Implement macOS-specific camera permissions handling
- Implement the `start_stream`, `stop_stream` and `_update` methods
- Test the module on different platforms (Windows, Linux, MacOS)
- Add more filters and effects
