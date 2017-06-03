"""
NVIDIA Mock Camera Driver
Used for testing and development

Author: Max Ferguson
License: MIT
"""
import numpy as np



def get_frame(debug=True):
    """
    Return a frame from the camera as a RGB numpy array
    Return None is no frame is available
    Throw an error if something has gone wrong

    @debug: Show the video feed from the camera
    @frame: A numpy array with dimensions [height,width,channels]
    """
    return np.random.randint(low=0, high=255, size=(360, 640, 3), dtype=int)



def close_pipeline():
    """
    Close the gstreamer pipeline
    """
    pass










