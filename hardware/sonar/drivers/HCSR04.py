"""
Measure the distance or depth with an HCSR04 Ultrasonic sound
sensor and a Raspberry Pi.
Imperial and Metric measurements are available"""
import time
import math
import logging
from builtins import range

# Setup a logger for this module
logger = logging.getLogger(__name__)


def is_falling_edge(current,previous):
    """
    Return True if the two points represent a falling edge
    """
    return current == 0 and previous == 1


def is_rising_edge(current,previous):
    """
    Return True if the two points represent a rising edge
    """
    return current == 1 and previous == 0



class HCSR04():
    """
    Create a measurement using a HC-SR04 Ultrasonic Sensor connected to
    the GPIO pins of a NVIDIA TX1.
    """
    max_distance_cm = 500 # cm

    def __init__(self, trig_pin, echo_pin, temperature=20):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.temperature = temperature

    def distance_cm(self, sample_size=11, sample_wait=0.1):
        """
        Return an error corrected unrounded distance, in cm, of an object
        adjusted for temperature in Celcius.  The distance calculated
        is the median value of a sample of `sample_size` readings.

        Speed of readings is a result of two variables.  The sample_size
        per reading and the sample_wait (interval between individual samples).
        Example: To use a sample size of 5 instead of 11 will increase the
        speed of your reading but could increase variance in readings;
        value = sensor.Measurement(trig_pin, echo_pin)
        r = value.raw_distance(sample_size=5)

        Adjusting the interval between individual samples can also
        increase the speed of the reading.  Increasing the speed will also
        increase CPU usage.  Setting it too low will cause errors.  A default
        of sample_wait=0.1 is a good balance between speed and minimizing
        CPU usage.  It is also a safe setting that should not cause errors.

        e.g.
        r = value.raw_distance(sample_wait=0.03)
        """

        speed_of_sound = 331.3 * math.sqrt(1+(self.temperature / 273.15))
        sample_timeout = 2 * self.max_distance_cm / speed_of_sound / 100
        sample = []

        for distance_reading in range(sample_size):
            time_passed = self.take_sample(sample_wait,sample_timeout)
            distance_cm = time_passed * ((speed_of_sound * 100) / 2)
            sample.append(distance_cm)
        sorted_sample = sorted(sample)
        return sorted_sample[sample_size // 2]


    def take_sample(self,sample_wait,sample_timeout):
        """
        Take a sonar reading
        Return the time required for the echo to bounce, or timeout
        Return 0 if the signal bounces back immediately
        """
        self.trig_pin.low()
        time.sleep(sample_wait)
        # Raise and lower the pin for 500 us
        self.trig_pin.pulse(100)
        # Start waiting for the reply
        start = time.time()
        duration = time.time()-start
        previous_state = self.echo_pin.get_value()
        # Loop until we see the echo
        while duration<sample_timeout:
            state = self.echo_pin.get_value()
            if is_falling_edge(state,previous_state):
                logger.debug("Received sonar signal")
                return duration
            if is_rising_edge(state,previous_state):
                logger.debug("Received sonar echo")
                return duration/2
            self.sleep_us(500)
            duration = time.time()-start
        # It took too long to receive the response
        logger.debug("Sonar timeout")
        return duration


    def sleep_us(self,duration):
        """
        Sleep for @duration (us)
        """
        return time.sleep(duration/10**6)


