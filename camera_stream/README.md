# Camera Stream Module

A Python module for streaming camera footage with adjustable filters that can be integrated with OBS and other streaming software.

## Features

- Camera streaming via Flask web server
- MJPEG stream format compatible with OBS and other streaming software
- Preview mode for testing camera setup
- Configurable host and port settings
- Support for camera source selection

## Installation

```bash
# Install required dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from camera_stream import CameraStream

# Initialize with default camera (index 0)
camera = CameraStream()

# Start streaming on localhost:7277
camera.start_stream()

# To stop the stream
camera.stop_stream()
```

### Command Line Interface

```bash
# Display help
python camera_stream --help

# Start stream with default settings
python camera_stream

# Test if camera is working
python camera_stream --test

# Preview camera in a window
python camera_stream --preview

# Stream with custom settings
python camera_stream --camera_source 1 --host 0.0.0.0 --port 8080 --open-browser
```

## Configuration Options

- `camera_source`: Camera index to use (default: 0)
- `host`: Host address to bind the server (default: 127.0.0.1)
- `port`: Port number for the server (default: 7277)
- `open-browser`: Automatically open browser to view stream

## Configuration File
Inside the filters directory, you'll find a [`filters_config.json`](filters/filters_config.json) file. This file contains the configuration for the filters.
Each filter has a description, parameters, and an enabled flag. You can enable or disable filters by setting the `enabled` flag to `true` or `false`.
> **Note**: The enabled flag is whether the filter will work when requested in the cli flags.

## Integration with OBS

Add a "Browser Source" in OBS and set the URL to `http://localhost:7277/` (or your configured host/port).
