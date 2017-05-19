from drivers.GPIO import Pin
from drivers.HCSR04 import HCSR04


class Sonar(object):
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
        Return the distance in mm
        If the distance is too large, the maximum is returned
        """
        try:
            return self.sensor.distance_mm()
        except OSError:
            print "No object detected"
            return self.sensor.MAX_RANGE_MM



class FrontSonar(Sonar):
    """
    The front sonar sensor on the STAR Car
    """
    # Input - J21 - Pin 31 - GPIO9_MOTION_INT
    echo_port = "J21"
    echo_pin = "31" 
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
    # Output - J21 - Pin 37 - GPIO8_ALS_PROX_INT
    tirgger_port = "J21"
    trigger_pin = "37"



if __name__=="__main__":
    f = FrontSonar()
    print f.distance()

