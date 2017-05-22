# Test Environment
# Interface between learning algorith and physical car
# Represents the worlrd as a MDP

import random
import math
import numpy as np
from ..q_learning.configs.linear import config
from hardware.car import car
from test import ActionSpace, ObservationSpace


class CarEnvironment(object):
    """
    Test         if action == 0:  # Left
            self.rotation = -0.2
            self.throttle = 0

        elif action == 1:  # Right
            self.rotation = 0.2
            self.throttle = 0

        elif action == 2:  # Forward
            self.rotation = 0
            self.throttle = 0.4

        elif action == 3:  # Backward
            self.throttle = -0.4
            self.rotation = 0environment
    """

    def __init__(self):
        self.steps = 0
        self.resets = 0
        self.sonar = [0,0]
        self.action_space = ActionSpace()
        self.observation_space = ObservationSpace()


    def render(self):
        """
        Render the environment
        """
        pass


    def reset(self):
        """
        Reset the environment
        Return the state
        """
        self.resets += 1
        car.reset()
        return self._get_state()


    def step(self,action):
        """
        Move the car.
        Return (new_state, reward, done, info) tuple
        """
        self._take_action(action)
        state = self._get_state()
        reward = self._get_reward(state)

        # Restart if it survives 1000 steps
        if self.steps%1000==0:
            done = True

        # Fail if it gets closer than 20 cm to an object
        if np.min(self.sonar)<20:
            done = True
            reward = -100

        # Call done hooks if needed
        if done:
            self.reset()

        self.steps += 0
        return (state,reward,done,False)


    def _get_state(self):
        """
        Return the current state
        """
        # Take measurements
        steering = car.steering.get_rotation()
        throttle = car.throttle.get_throttle()
        rear_sonar = car.rear_sonar.distance()
        front_sonar = car.front_sonar.distance()
        # Store measurements
        self.sonar = [front_sonar,rear_sonar]
        controls = [steering,throttle]
        state = np.array(self.sonar+controls)
        return state[None,:,None]


    def _get_reward(self,state):
        """
        Return the current reward.
        @state is a object describing the car state
        """
        reward = 0
        reward += 0.1 * abs(car.steering.get_rotation())
        reward += 0.4 * car.throttle.get_throttle()
        reward += 0.1 * min(np.min(self.sonar)-30, 0)
        return reward


    def _take_action(self,action):
        """
        Apply a particular action on the real car
        """
        if action == 0:  # Left
            rotation = -0.2
            throttle = 0

        elif action == 1:  # Right
            rotation = 0.2
            throttle = 0

        elif action == 2:  # Forward
            rotation = 0
            throttle = 0.4

        elif action == 3:  # Backward
            throttle = -0.4
            rotation = 0

        car.steering.update_rotation(rotation)
        car.throttle.update_thottle(throttle)

