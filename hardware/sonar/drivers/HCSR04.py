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


class HCSR04():
    """
    Create a measurement using a HC-SR04 Ultrasonic Sensor connected to
    the GPIO pins of a Raspberry Pi.
    Metric values are used by default. For imperial values use
    unit='imperial'
    temperature=<Desired temperature in Fahrenheit>
    """
    max_distance_cm = 5000 # cm

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
        sample_timeout = self.max_distance_cm / speed_of_sound / 100
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
        self.trig_pin.high()
        self.sleep_us(10)
        self.trig_pin.low()
        # Check if the echo has already bounced back
        sonar_started = time.time()
        if self.echo_pin.get_value()==0:
            logger.debug("Sonar already bounced")
            return 0
        # Wait for the sonar to return
        while self.echo_pin.get_value()==1:
            duration = time.time() - sonar_started
            if duration>sample_timeout:
                logger.debug("Sonar timeout")
                return duration
            self.sleep_us(1000)
        # The sigal has returned
        return time.time() - sonar_started


    def sleep_us(self,duration):
        """
        Sleep for @duration (us)
        """
        return time.sleep(duration/10**6)


