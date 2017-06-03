"""
Public interface to the NVIDIA Camera
Uses NVIDIA GPU acceleration to resize the camera image for learning

Author: Max Ferguson
License: MIT
"""
from .drivers import TX1



class Camera:
    """
    An interface to the NVIDIA camera
    Return camera frames as numpy arrays
    """

    def __del__(self):
        """
        Free up the camera pipeline
        """
        TX1.close_pipeline()

    def get_frame(self):
        """
        Return a camera frame as a numpy array
        """
        frame = None
        while frame is None:
            frame = TX1.get_frame()
        return frame
