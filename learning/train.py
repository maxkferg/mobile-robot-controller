import argparse
import tensorflow as tf
from .configs import ddpg as ddpg_config
from .configs import qlearning as qlearning_config
from .environments import continuous, discrete
from .algorithms.qlearning.linear import QNetwork
from .algorithms.vision import ddpg


def train_car_qlearning():
    """
    Train a q-learning agent using the simulation
    """
    config = qlearning_config.linear
    env = RealEnvironment()
    tf.reset_default_graph()
    model = Linear(env, config, resume=False)
    model.run(exp_schedule, lr_schedule)



def train_simulation_qlearning():
    """
    Train a q-learning agent using the simulation
    """
    config = qlearning_config.linear

    # Create simulated enviroment with discrete action space
    env = discrete.SimulatedEnvironment(draw=config.draw)

    # train
    model = Linear(env, config)
    model.run()



def train_simulation_ddpg():
    """
    Train a ddpg agent using the simulation
    """
    train_indicator = 1
    config = ddpg_config.simulation
    env = continuous.SimulatedEnvironment(render=config.render) 
    ddpg.vision_train(env, config, train_indicator)



def train_car_ddpg():
    """
    Train a ddpg agent using the simulation
    """
    train_indicator = 1
    config = ddpg_config.simulation
    env = continuous.RealEnvironment(render=config.render)
    ddpg.vision_train(env, config, train_indicator)

