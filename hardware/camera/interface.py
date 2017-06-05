"""
Public interface to the NVIDIA Camera
Uses NVIDIA GPU acceleration to resize the camera image for learning

Author: Max Ferguson
License: MIT
"""
import os

# Load module depending on development
if os.environ.get('DEV'):
    from .drivers import Mock as TX1
else:
    from .drivers import TX1


class Camera:
    """
    An interface to the NVIDIA camera
    Return camera frames as numpy arrays
    """
    image_shape  = (180, 320, 3)

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
