import os
import logging
import numpy as np
from .drivers.GPIO import Pin, MockPin
from .drivers.HCSR04 import HCSR04

# Setup a logger for this module
logger = logging.getLogger(__name__)

# Change the class for development
if os.environ.get('DEV'):
    Pin = MockPin


class Sonar():
    """
    A sonar sensor on the Car

    Use Sonar.tick to run the sonar
    After running Sonar.tick multiple times, run Sonar.distance to get the distance
    """
    echo_port = None
    echo_pin = None
    trigger_port = None
    trigger_pin = None
    sonar_sample_size = 3
    sonar_sample_wait = 0.01

    def __init__(self):
        trigger = Pin(self.trigger_port, self.trigger_pin, is_out=True)
        echo = Pin(self.echo_port, self.echo_pin, is_out=False)
        self.sensor = HCSR04(trigger, echo)
        self.buffer = []


    def tick(self):
        """
        Take a single sonar reading. Add it to the reading buffer
        """
        samples = 1
        while len(self.buffer) < self.sonar_sample_size+1:
            distance = self.sensor.distance_meters(samples, self.sonar_sample_wait)
            self.buffer.insert(0,distance)
        self.buffer.pop()


    def distance(self):
        """
        Return the distance in meters.
        Uses the reading buffer to estimate the current distance
        """
        sorted_distance = sorted(self.buffer)
        distance = sorted_distance[self.sonar_sample_size // 2]
        logger.info("{0} distance = {1:.2f} m".format(self.sensor_name, distance))
        return distance



class FrontSonar(Sonar):
    """
    The front sonar sensor on the STAR Car
    """
    # Input - J21 - Pin 31 - GPIO11_AP_WAKE_BT
    echo_port = "J21"
    echo_pin = "33"
    # Output - J21 - Pin 37 - GPIO8_ALS_PROX_INT
    trigger_port = "J21"
    trigger_pin = "37"
    sensor_name = "FrontSonar"



class RearSonar(Sonar):
    """
    The rear sonar sensor on the STAR Car
    """
    # Input - J21 - Pin 31 - GPIO9_MOTION_INT
    echo_port = "J21"
    echo_pin = "31"
    # Output - J21 - Pin 29 - GPIO19_AUD_RST
    trigger_port = "J21"
    trigger_pin = "29"
    sensor_name = "RearSonar"
