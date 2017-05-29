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
import numpy as np
from builtins import range
from hardware.car import car
from .utils.buffer import VectorBuffer
from .simulation.car import CarSimulation


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
    shape = (20,1)


class ContinuousEnvironment:
    """
    Continuous simulated environment
    Base class for simulated and real implimentations
    """
    action_history = 50
    state_history = 5
    action_space = ActionSpace()
    observation_space =  ObservationSpace()

    def __init__(self, render=False, seed=0):
        self.steps = 0
        self.resets = 0
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
        state = self._get_current_state()
        reward = self._get_reward(state)
        done = self._is_done(state)

        self.action_history.add(action)
        self.state_history.add(state)
        self.steps += 1

        if done:
            self.reset()

        state_with_history = self.state_history.to_array()
        return (state_with_history,reward,done,False)


    def reset(self):
        """
        Reset the environment
        """
        self.car.reset()
        self.resets += 1
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
        if any(sonar<20):
            return True


    def _is_done(self,state):
        """
        Return True if this episode is done
        """
        if self._is_crashed(state):
            print("Crashed")
            return True
        if self.steps % 500==0:
            print("Survived 500 steps")
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
            return -1 - 5 * abs(throttle)
        # Calculate reward
        reward = 0
        reward += 1.0 * max(0, throttle) # Favor driving forward
        reward += 0.1 * min(0, throttle) # Penalize reversing
        reward -= 10.0 * abs(np.mean(steering_history)) # Favor driving straight
        reward += 0.01 * np.sum(np.log(sonar)) # Favor larger sonar values
        assert isinstance(reward,float)
        return reward





class SimulatedEnvironment(ContinuousEnvironment):
    """
    Continuous simulated environment

    Uses pygame simulation to generate the state vector
    """
    def __init__(self, render=False, seed=0):
        """
        Initialize the simulation
        """
        super().__init__(render,seed)
        self.car = CarSimulation(render=True)


    def render(self):
        """
        Render the environment
        """
        self.car.render()


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
        rear_sonar = self.car.rear_sonar
        front_sonar = self.car.front_sonar
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
        rear_sonar = self.car.rear_sonar.distance()
        front_sonar = self.car.front_sonar.distance()
        # Create R3 state vector representation
        return [steering,throttle,front_sonar,rear_sonar]






