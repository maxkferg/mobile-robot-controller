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
from hardware.car import car
from .utils.buffer import VectorBuffer
from .simulation.car import CarSimulation

# Setup a logger for this module
logger = logging.getLogger(__name__)


def normalize_sonar(sonar):
    """
    Normalize the sonar values before adding them to the state
    The NN is initialized assuming that the state values are about 1
    Normalizing the sonar helps to improve the initial policy
    """
    print(sonar/100)
    return sonar/100 # Convert to meters


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
    shape = (40,1)


class ContinuousEnvironment:
    """
    Continuous simulated environment
    Base class for simulated and real implimentations
    """
    action_history = 50
    state_history = 10
    action_space = ActionSpace()
    observation_space =  ObservationSpace()

    def __init__(self, render=False, seed=0):
        self.steps = 0
        self.resets = 0
        self.should_render = render
        self.state_history = VectorBuffer((self.state_history, 4))
        self.action_history = VectorBuffer((self.action_history, 2))
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
        reward = self._get_reward(state)
        done = self._is_done(state)

        self.action_history.add(action)
        self.state_history.add(state)
        self.steps += 1

        state_with_history = self.state_history.to_array()
        print(self.state_history.to_array())
        return (state_with_history,reward,done,False)


    def reset(self):
        """
        Reset the environment
        """
        self.car.reset()
        self.resets += 1
        self.action_history.clean()
        self.state_history.clean()
        self.state_history.add(self._get_current_state())
        return self.state_history.to_array()


    def close(self):
        """
        Terminate the environment
        """
        pass


    def _is_crashed(self,state):
        """
        Return True if we think the car is crashed
        """
        sonar = np.array(state[2:4])
        if any(sonar<0.2):
            return True


    def _is_done(self,state):
        """
        Return True if this episode is done
        """
        if self._is_crashed(state):
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


    def _get_reward(self,state):
        """
        Return the reward associated with @state
        @param state: An object describing the car state
        """
        # Extract state parameters
        rotation = state[0]
        throttle = state[1]
        sonar = state[2:4]
        steering_history = self.action_history.to_array()[:,0]
        # Penalize collisions heavily
        if self._is_crashed(state):
            return -1 - 1 * abs(throttle)
        # Calculate reward
        reward = 0
        reward += 0.004 * max(0, throttle) # Favor driving forward
        reward += 0.001 * min(0, throttle) # Penalize reversing
        reward += 0.001 * abs(rotation) # Penalize turning
        reward += 0.0001 * np.sum(sonar) # Favor larger sonar values
        assert isinstance(reward,float)
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
        logger.info("Environment Reset")
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
        rear_sonar = normalize_sonar(self.car.rear_sonar)
        front_sonar = normalize_sonar(self.car.front_sonar)
        # Create R3 state vector representation
        return [steering,throttle,front_sonar,rear_sonar]




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
        Wait for a manual reset
        """
        state = super().reset()
        raw_input("Press enter to continue training?")
        return state


    def _take_action(self,action):
        """
        Apply a particular action on the real car
        """
        self.car.steering.set_rotation(action[0])
        self.car.throttle.set_throttle(action[1])


    def _get_current_state(self):
        """
        Return the current state
        """
        # Take measurements
        steering = self.car.steering.get_rotation()
        throttle = self.car.throttle.get_throttle()
        rear_sonar = normalize_sonar(self.car.rear_sonar.distance())
        front_sonar = normalize_sonar(self.car.front_sonar.distance())
        # Create R3 state vector representation
        return [steering,throttle,front_sonar,rear_sonar]






