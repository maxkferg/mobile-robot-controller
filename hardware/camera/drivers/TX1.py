"""
NVIDIA Camera Driver
Uses NVIDIA GPU acceleration to resize the camera image for learning

Author: Max Ferguson
License: MIT
"""
import sys
import gi
import numpy
import logging
gi.require_version('Gst', '1.0')
from gi.repository import Gst

logger = logging.getLogger(__name__)

Gst.init(None)

image_arr = None


def gst_to_opencv(sample):
    """
    Return the image as a numpy array
    @sample. A sample from gstreamer
    """
    buf = sample.get_buffer()
    caps = sample.get_caps()
    logger.debug(caps.get_structure(0).get_value('format'))
    logger.debug(caps.get_structure(0).get_value('height'))
    logger.debug(caps.get_structure(0).get_value('width'))
    logger.debug(buf.get_size())

    arr = numpy.ndarray(
        (caps.get_structure(0).get_value('height'),
         caps.get_structure(0).get_value('width'), 3),
        buffer=buf.extract_dup(0, buf.get_size()),
        dtype=numpy.uint8)
    return arr


def new_buffer(sink, data):
    """
    Accept a new buffer from gstreamer
    @sink. A gstreamer sink object
    @data. Unknown
    """
    global image_arr
    sample = sink.emit("pull-sample")
    arr = gst_to_opencv(sample)
    image_arr = arr
    return Gst.FlowReturn.OK



pipeline = Gst.parse_launch("nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)360,format=(string)I420, framerate=(fraction)120/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink name=sink")
logger.info("Camera Pipeline open")
sink = pipeline.get_by_name("sink")
logger.debug("Camera sink created")

if not sink or not pipeline:
    logger.error("Not all elements could be created.")
    exit(-1)

sink.set_property("emit-signals", True)
#sink.set_property("max-buffers", 2)
sink.set_property("drop", True)
sink.set_property("sync", False)
sink.connect("new-sample", new_buffer, sink)

# Start playing
ret = pipeline.set_state(Gst.State.PLAYING)
if ret == Gst.StateChangeReturn.FAILURE:
    print("Unable to set the pipeline to the playing state.")
    exit(-1)

# Wait until error or EOS
bus = pipeline.get_bus()


def get_frame(debug=False):
    """
    Return a frame from the camera as a RGB numpy array
    Return None is no frame is available
    Throw an error if something has gone wrong

    @debug: Show the video feed from the camera
    @frame: A numpy array with dimensions [height,width,channels]
    """
    message = bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
    if debug and image_arr is not None:   
        import cv2
        cv2.imshow("appsink image arr", image_arr)
        cv2.waitKey(1)
    if message:
        if message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error received from element %s: %s" % (
                message.src.get_name(), err))
            print("Debugging information: %s" % debug)
            raise IOError("NVIDIA Camera Error")
        elif message.type == Gst.MessageType.EOS:
            print("End-Of-Stream reached.")
            raise IOError("NVIDIA Camera Error")
        elif message.type == Gst.MessageType.STATE_CHANGED:
            if  isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                print("Pipeline state changed from %s to %s." %
                       (old_state.value_nick, new_state.value_nick))
        else:
            print("Unexpected message received.")
    return image_arr



def close_pipeline():
    """
    Close the gstreamer pipeline
    """
    pipeline.set_state(Gst.State.NULL)










