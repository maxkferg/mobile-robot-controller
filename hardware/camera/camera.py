"""
basic-tutorial-2: GStreamer concepts
http://docs.gstreamer.com/display/GstSDK/Basic+tutorial+2%3A+GStreamer+concepts
"""

import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import numpy

Gst.init(None)

image_arr = None

def gst_to_opencv(sample):
    buf = sample.get_buffer()
    caps = sample.get_caps()
    #print(caps.get_structure(0).get_value('format'))
    #print(caps.get_structure(0).get_value('height'))
    #print(caps.get_structure(0).get_value('width'))
    #print(buf.get_size())

    arr = numpy.ndarray(
        (caps.get_structure(0).get_value('height'),
         caps.get_structure(0).get_value('width'),
         3),
        buffer=buf.extract_dup(0, buf.get_size()),
        dtype=numpy.uint8)
    return arr

def new_buffer(sink, data):
    global image_arr
    sample = sink.emit("pull-sample")
    # buf = sample.get_buffer()
    # print "Timestamp: ", buf.pts
    arr = gst_to_opencv(sample)
    image_arr = arr
    return Gst.FlowReturn.OK

pipeline = Gst.parse_launch("nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)360,format=(string)I420, framerate=(fraction)120/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink name=sink")

print("Pipeline open")

sink = pipeline.get_by_name("sink")

if not sink or not pipeline:
    print("Not all elements could be created.")
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


# Parse message
def loop():
    import cv2
    message = bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
    if image_arr is not None:   
        print(image_arr.shape)
        print(image_arr[1,1,1])
        cv2.imshow("appsink image arr", image_arr)
        cv2.waitKey(1)
    if message:
        if message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error received from element %s: %s" % (
                message.src.get_name(), err))
            print("Debugging information: %s" % debug)
            return False
        elif message.type == Gst.MessageType.EOS:
            print("End-Of-Stream reached.")
            return False
        elif message.type == Gst.MessageType.STATE_CHANGED:
            if  isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                print("Pipeline state changed from %s to %s." %
                       (old_state.value_nick, new_state.value_nick))
        else:
            print("Unexpected message received.")
    return True


running = True
try:
    while running:
        running = loop()
finally:
    # Free resources
    pipeline.set_state(Gst.State.NULL)















