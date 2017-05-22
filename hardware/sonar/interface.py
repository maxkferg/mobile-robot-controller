import os
import numpy as np
from .drivers.GPIO import Pin, MockPin
from .drivers.HCSR04 import HCSR04

# Change the class for development
if os.environ.get('DEV'):
    Pin = MockPin



class Sonar():
    """
    A sonar sensor on the Car
    """
    echo_port = None
    echo_pin = None
    trigger_port = None
    trigger_pin = None

    def __init__(self):
        trigger = Pin(self.trigger_port, self.trigger_pin, is_out=True)
        echo = Pin(self.echo_port, self.echo_pin, is_out=False)
        self.sensor = HCSR04(trigger, echo)

    def distance(self):
        """
        Return the distance in cm
        Takes 11 sensor readings and returns the result
        If the distance is too large, the maximum is returned
        """
        return self.sensor.distance_cm()



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



if __name__=="__main__":
    command = None
    front = FrontSonar()
    back = BackSonar()
    while True:
        print("Front: {0}".format(front.distance()))
        print("Back: {0}".format(back.distance()))

