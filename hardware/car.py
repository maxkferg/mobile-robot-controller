"""
Represents all of the controls for the car
"""
from motors import Throttle, Steering
from sonar import FrontSonar, RearSonar

class Car(object):

    def __init__(self):
        """
        Start up all the sensors
        """
        self.steering = Steering()
        self.throttle = Throttle()
        self.front_sonar = FrontSonar()
        self.rear_sonar = RearSonar()

    def reset(self):
        """
        Reset the car controllers
        """
        self.steering.reset()
        self.throttle.reset()


car = Car()