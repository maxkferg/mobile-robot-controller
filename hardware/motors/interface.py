import os,time
from builtins import range
from .drivers import Mock,PCA9685


if os.environ.get('DEV'):
    PCA9685 = Mock


class PWM(object):
    """
    Pulse width modulation (controller)
    """
    frequency = 100 # Hz
    resolution = 4096 # Bits

    def __init__(self, i2cbus, channel):
        """
        Initialize the hardware
        """
        self.channel = channel
        self.pulse_length = 0
        self.controller = PCA9685(busnum=i2cbus)
        self.controller.set_pwm_freq(self.frequency)

    def set_pulse_length(self, length):
        """
        Set the length of the PWM pulse length (in ms)
        """
        print('{0}: changing pulse length to {1} ms'.format(self,length))
        total_period = 1000/self.frequency
        pulse_bits = int(self.resolution * length / total_period)
        print('{0}: changing pulse length to {1}/{2} bits'.format(self, pulse_bits, self.resolution))
        self.controller.set_pwm(self.channel, 0, pulse_bits)
        self.pulse_length = length

    def get_pulse_length(self, length):
        """
        Return the length of the pulse
        """
        return self.pulse_length



class Steering(PWM):
    """
    Control the steering of the car
    Provides an abstraction over the hardware, allowing direction to be set on a -1.0 to 1.0 scale.
    The steering direction is expressed numerically:
     * 0.0 left turn
     * 0.5 straight
     * 1.0 right turn
    """
    i2cbus = 0 # I2C bus 0
    channel = 7 # PWM channel 7
    min_rotation = -1.0
    max_rotation = 1.0
    default_rotation = 0.0
    pwm_min_pulse = 1.0 # ms
    pwm_max_pulse = 2.0 # ms


    def __init__(self):
        """
        Intialize the hardware and turn the wheels to the default position
        """
        super(Steering, self).__init__(self.i2cbus, self.channel)
        self.rotation = self.default_rotation
        self.reset() # set the PWM to match default_rotation


    def __str__(self):
        """Return the name of the class"""
        return "Steering ({0})".format(self.channel)


    def turn_left(self,amount=0.1):
        """
        Turn the car left by @amount
        """
        return self.update_rotation(-amount)


    def turn_right(self,amount=0.1):
        """
        Turn the car right by @amount
        """
        return self.update_rotation(amount)


    def reset(self):
        """
        Return to the default throttle position
        """
        self.update_rotation(self.default_rotation-self.rotation)


    def get_rotation(self):
        """
        Return the current rotation
        """
        return self.rotation


    def update_rotation(self,amount):
        """
        Rotate the car steering system by @amount. Return the current rotation

        A negative amount corroponds to a left turn.
        We deliberately prevent the AI from setting the actual angle, to avoid
        very rapid changes in angle.
        """
        self.rotation += amount
        self.rotation = max(self.rotation, self.min_rotation)
        self.rotation = min(self.rotation, self.max_rotation)
        print('{0}: changing steering to {1}'.format(self,self.rotation))
        gradient = (self.pwm_max_pulse - self.pwm_min_pulse)/(self.max_rotation - self.min_rotation)
        pulse = self.rotation*gradient + self.pwm_min_pulse - gradient*self.min_rotation
        assert pulse >= self.pwm_min_pulse
        assert pulse <= self.pwm_max_pulse
        self.set_pulse_length(pulse)
        return self.rotation




class Throttle(PWM):
    """
    Control the throttle of the car
    Provides an abstraction over the hardware, allowing direction to be set on a -1.0 to 1.0 scale.
    The throttle is expressed numerically:
     * 0.0 backwards
     * 0.5 stationary
     * 1.0 right turn
    """
    i2cbus = 0 # I2C bus 0
    channel = 6 # PWM channel 6
    min_throttle = -1.0
    max_throttle = 1.0
    default_throttle = 0.0
    pwm_min_pulse = 1.0 # ms
    pwm_max_pulse = 2.0 # ms


    def __init__(self,):
        """
        Intialize the hardware and turn the wheels to the default position
        """
        super(self.__class__, self).__init__(self.i2cbus, self.channel)
        self.throttle = self.default_throttle
        self.reset() # set the PWM to match default_rotation


    def __str__(self):
        """Return the name of the class"""
        return "Throttle ({0})".format(self.channel)


    def accelerate(self,amount=0.1):
        """
        Slow the car by @amount
        """
        self.update_thottle(amount)


    def decelerate(self,amount=0.1):
        """
        Accelerate the car by @amount
        """
        self.update_thottle(-amount)


    def reset(self):
        """
        Return to the default throttle position
        """
        self.update_thottle(self.default_throttle-self.throttle)


    def get_throttle(self):
        """
        Return the current (limited) speed
        """
        return self.throttle


    def limit_throttle(self,speed):
        """
        Return the new (limited) speed
        """

        forward_max = 0.60
        backward_max = -0.60

        if speed < backward_max:
            return backward_max
        if speed > forward_max:
            return forward_max
        return speed


    def limit_pwm(self,pulse):
        """
        Return the new limited PWM
        Certain PWM frequencies will cause damage, so we block them
        """
        pwm_stall_min = 1.35 # ms
        pwm_stall_max = 1.65 # ms
        pwm_stopped = 1.50 # ms
        if pwm_stall_min < pulse and pulse < pwm_stall_max:
            pulse = pwm_stopped
        assert pulse >= self.pwm_min_pulse # Sanity check
        assert pulse <= self.pwm_max_pulse # Sanity check
        return pulse


    def update_thottle(self,amount):
        """
        Update the throttle of the main motor by @amount

        A negative amount corroponds to a left turn.
        We deliberately prevent the AI from setting the actual throttle, to avoid
        very rapid changes.
        """
        self.throttle = self.limit_throttle(self.throttle+amount)
        print('{0}: changing throttle to {1}'.format(self,self.throttle))
        gradient = (self.pwm_max_pulse - self.pwm_min_pulse)/(self.max_throttle - self.min_throttle)
        pulse = self.throttle * gradient + self.pwm_min_pulse - gradient*self.min_throttle
        pulse = self.limit_pwm(pulse)
        self.set_pulse_length(pulse)
        return self.throttle






if __name__=='__main__':
    throttle = Throttle()
    steering = Steering()

    # Accelerate backwards
    print('--------------- backwards ---------------')
    for i in range(10):
        throttle.decelerate(amount=0.1)

    # Accelerate forwards
    print('--------------- forwards ---------------')
    for i in range(20):
        throttle.accelerate(amount=0.1)

    # Stop the car
    print('--------------- stop ---------------')
    throttle.reset()

    # Turn left
    print('--------------- left ---------------')
    for i in range(10):
        steering.turn_left(amount=0.1)

    # Turn right
    print('--------------- right ---------------')
    for i in range(20):
        steering.turn_right(amount=0.1)

    # Reset turning
    print('--------------- reset ---------------')
    steering.reset()








