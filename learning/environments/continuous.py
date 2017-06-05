"""
Continuous environments for the autonomous car

In these environments the car specifies a throttle value between -1.0 and 1.0, and a
steering angle value between -1.0 and 1.0.

The action space is represented as a R2 vector:

A = [[ steering
       throttle
    ]]


The state space is represented as a R4 vector:

S = [[ steering
       throttle
       front sonar
       rear sonar
    ]]
"""

import sys
import math
import time
import math
import random
import logging
import numpy as np
from builtins import range
from hardware.car import CarState, car
from hardware.camera import Camera
from .utils.buffer import VectorBuffer
from .simulation.car import CarSimulation

# Setup a logger for this module
logger = logging.getLogger(__name__)


class ActionSpace:
    """
    Represents the actions which can be taken
    """
    low = -1.0
    high = 1.0
    shape = (2,1)

    def sample(self):
        return np.random.uniform(low=0.0, high=1.0, size=self.shape)


class ObservationSpace:
    """
    Represents the observations which can be made
    """
    shape = (360, 640, 3)


class ContinuousEnvironment:
    """
    Continuous simulated environment
    Base class for simulated and real implimentations
    """
    action_history_size = 50
    sensor_history_size = 10
    action_space = ActionSpace()
    observation_space = ObservationSpace()

    def __init__(self, render=False, seed=0):
        self.steps = 1
        self.resets = 0
        self.should_render = render
        self.sensor_history = VectorBuffer((self.sensor_history_size, 4))
        self.action_history = VectorBuffer((self.action_history_size, 2))
        self.seed(seed)


    def seed(self,seed):
        """
        Set the environment seed
        """
        self.random_seed = seed


    def render(self):
        """
        Render the environment. Extended by child classes
        """
        pass


    def step(self,action):
        """
        Move the car
        """
        self._take_action(action)
        self.render()
        state = self._get_current_state()
        crashed = self._is_crashed(state) 
        reward = self._get_reward(state,crashed)
        done = self._is_done(state,crashed)

        self.action_history.add(action)
        self.sensor_history.add(state.sensors)
        self.steps += 1

        return (state, reward, done, False)


    def reset(self):
        """
        Reset the environment
        Return the current camera image
        """
        state = self._get_current_state()
        self.car.reset()
        self.resets += 1
        self.action_history.clean()
        self.sensor_history.clean(state.sensors)
        print("Environment Reset")
        return state


    def close(self):
        """
        Terminate the environment
        """
        pass


    def _is_crashed(self,state):
        """
        Return True if we think the car is crashed
        """
        threshold = 0.2
        return state.front_distance<threshold or state.rear_distance<threshold


    def _is_done(self,state,crashed):
        """
        Return True if this episode is done
        """
        if crashed:
            logger.info("CRASHED")
            return True
        if self.steps % 500==0:
            logger.info("Survived 500 steps")
            return True
        return False


    def _take_action(self,action):
        """
        Apply a particular action to the car
        """
        raise NotImplementedError


    def _get_current_state(self):
        """
        Return the current state
        """
        raise NotImplementedError


    def _get_reward(self,state,crashed):
        """
        Return a reward based on the average color in the camera
        """
        reward = np.mean(state.frames)/256
        reward = int(reward>0.46) + reward
        return reward



class SimulatedEnvironment(ContinuousEnvironment):
    """
    Continuous simulated environment

    Uses pygame simulation to generate the state vector
    """
    def __init__(self, render, seed=0):
        """
        Initialize the simulation
        """
        super().__init__(render,seed)
        self.car = CarSimulation()


    def render(self):
        """
        Render the environment
        """
        if self.should_render:
            self.car.render()
        elif self.resets%10==0:
            self.car.render()


    def reset(self):
        """
        Notify the user that the simulation has been reset
        """
        return super().reset()


    def _take_action(self, action):
        """
        Execute a certain action
        """
        self.car.frame_step(action)


    def _get_current_state(self):
        """
        Return the current state as a numpy array
        """
        # Take measurements
        steering = self.car.steering
        throttle = self.car.throttle
        rear_distance = self.car.rear_sonar
        front_distance = self.car.front_sonar
        frames = np.random.randint(low=0, high=255, size=Camera.image_shape, dtype=int)
        # Return a simulated variant on the real car state
        return CarState(steering,throttle,front_distance,rear_distance,frames)



class RealEnvironment(ContinuousEnvironment):
    """
    Continuous real environment

    Uses real car hardware to generate state vector
    """

    def __init__(self, render=False, seed=0):
        """
        Initialize the car hardware
        """
        super().__init__(render,seed)
        self.car = car


    def reset(self):
        """
        Notify the user that the simulation has been reset
        """
        return super().reset()


    def _take_action(self,action):
        """
        Apply a particular action on the real car
        """
        self.car.steering.set_rotation(action[0])
        self.car.throttle.set_throttle(action[1])


    def _is_crashed(self,state,n=3):
        """
        Check for crashed events
        """
        return False


    def _get_current_state(self):
        """
        Return the current state
        """
        return self.car.get_state()






