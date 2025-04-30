import sounddevice as sd
import numpy as np
import queue
import threading

class Sound:
    def __init__(self):
        """
        """
        pass

    def test_sound(self):
        """
        Test the sound analysis functionality
        """

        print(sd.query_devices(kind='input'))
        print(sd.query_devices(kind='output'))
