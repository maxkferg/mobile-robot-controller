"""
Represents all of the controls for the car
"""
from builtins import object
from .camera import Camera
from .motors import Throttle, Steering
from .sonar import FrontSonar, RearSonar


class CarState:
    """
    Compact representation of the car state
    """
    def __init__(self,steering,throttle,front_distance,rear_distance,frames):
        self.steering = steering
        self.throttle = throttle
        self.front_distance = front_distance
        self.rear_distance = rear_distance
        self.sensors = [steering, throttle, front_distance, rear_distance]
        self.frames = frames


class Car:
    """
    Public interface to the car hardware
    """
    def __init__(self):
        """
        Start up all the sensors
        """
        self.steering = Steering()
        self.throttle = Throttle()
        self.camera = Camera()
        self.front_sonar = FrontSonar()
        self.rear_sonar = RearSonar()


    def get_state(self):
        """
        Return the car state as a CarState object
        """
        for i in range(self.front_sonar.sonar_sample_size):
            self.front_sonar.tick()
            self.rear_sonar.tick()
        frame = self.camera.get_frame()
        front_distance = self.front_sonar.distance()
        rear_distance = self.rear_sonar.distance()
        throttle = self.throttle.get_throttle()
        steering = self.steering.get_rotation()
        return CarState(steering, throttle, front_distance, rear_distance, frame)


    def reset(self):
        """
        Reset the car controllers
        """
        self.throttle.reset()


car = Car()