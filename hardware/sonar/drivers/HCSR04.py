import time

class HCSR04(object):
    """
    Driver to use the untrasonic sensor HC-SR04.
    The sensor range is between 2cm and 4m.
    The timeouts received listening to echo pin are converted to OSError('Out of range')
    """
    # Timeout is based in chip range limit (400cm)
    MAX_RANGE_CM = 400
    MAX_RANGE_MM = 4000
    TIMEOUT_US = 500.0*2*30/1000

    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=None):
        """
        trigger_pin: Output pin to send pulses
        echo_pin: Readonly pin to measure the distance. The pin should be protected with 1k resistor
        echo_timeout_us: Timeout in microseconds to listen to echo pin. 
        By default is based in sensor limit range (4m)
        """
        self.echo_timeout_us = echo_timeout_us or self.TIMEOUT_US
        self.trigger = trigger_pin
        self.trigger.low()
        self.echo = echo_pin




    def _send_pulse_and_wait(self):
        """
        Send the pulse to trigger and listen on echo pin.
        We use the method `machine.time_pulse_us()` to get the microseconds until the echo is received.
        """
        self.trigger.low() # Stabilize the sensor
        time.sleep(5.0/10**6)
        self.trigger.high()
        # Send a 10us pulse.
        time.sleep(5.0/10**6)
        self.trigger.low()
        try:
            return self._wait_for_pulse(self.echo, self.echo_timeout_us)
        except OSError as ex:
            if ex.args[0] == 110: # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex




    def _wait_for_pulse(self,listener,timeout):
        """
        Wait for a high in listener until timeout
        @timeout. The timeout in us
        """
        start = time.time()
        duration = 10**6*(time.time() - start)
        while duration < timeout:
            duration = 10**6*(time.time() - start)
            print "current listener value",listener.get_value()
            if listener.get_value():
                return duration
            time.sleep(1.0/10**6)
        raise OSError(110)




    def distance_mm(self):
        """
        Get the distance in milimeters without floating point operations.
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.34320 mm/us that is 1mm each 2.91us
        # pulse_time // 2 // 2.91 -> pulse_time // 5.82 -> pulse_time * 100 // 582 
        mm = pulse_time * 100.0 // 582
        return mm




    def distance_cm(self):
        """
        Get the distance in centimeters with floating point operations.
        It returns a float
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.034320 cm/us that is 1cm each 29.1us
        cms = (pulse_time / 2) / 29.1
        return cms
