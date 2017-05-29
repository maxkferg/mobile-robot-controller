
"""
Discrete environments for the autonomous car

In these environments the car specifies a throttle value between -1.0 and 1.0, and a 
steering angle value between -1.0 and 1.0.

The action space is a discrete set of actions

A = {1,2,3,4}

 
The state space is represented as a R4 vector:

S = [[ steering
       throttle
       front sonar
       rear sonar
    ]] 
"""


import random
import math
import numpy as np
from . import continuous

class ActionSpace:
    """
    Represents the actions which can be taken
    """
    low = 0
    high = 4
    shape = (1,1)

    def sample(self):
        return random.randint(self.low, self.high)

    def as_continuous(self,action):
        """
        Return the equivalent action in a continuous (R2) action space
        """
        if action == 0:  # Left
            steering = -0.4
            throttle = 0.3
        
        elif action == 1:  # Right
            steering = 0.4
            throttle = 0.3
        
        elif action == 2:  # Forward
            steering = 0
            throttle = 0.4
        
        elif action == 3:  # Backward
            steering = 0
            throttle = -0.4

        return [steering,throttle]



class ObservationSpace:
    """
    Represents the observations which can be made
    """
    shape = (4,1)



class SimulatedEnvironment(continuous.SimulatedEnvironment):
    """
    Discrete simulated environment

    Uses pygame simulation to generate the state vector
    """
    action_space = ActionSpace()
    observation_space =  ObservationSpace()

    def _take_action(self, action):
        """
        Execute a certain action
        """
        action = self.action_space.as_continuous(action)
        return super()._take_action(action)
  



class RealEnvironment(continuous.RealEnvironment):
    """
    Discrete real environment

    Uses real car hardware to generate state vector 
    """
    action_space = ActionSpace()
    observation_space =  ObservationSpace()

    def _take_action(self,action):
        """
        Apply a particular action on the real car
        """
        action = self.action_space.as_continuous(action)
        return super()._take_action(action)
        





