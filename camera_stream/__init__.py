"""
Camera streaming module for festival projects.

This module provides functionality to stream from a camera, 
apply adjustments to footage, and make it available on a flask website.
"""

from .core import CameraStream
from .utils.sound_utils import Sound
from .utils.camera_utils import Camera

from .filters import *

__version__ = "0.1.0"