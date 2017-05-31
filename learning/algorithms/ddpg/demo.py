"""
Test the DDPG Network on a simple Gym environment
"""
import os
import gym
import tensorflow as tf
from gym import wrappers
from datetime import datetime
from .core.ddpg import DDPG


def demo(config):
    """
    Run the DDPG Demo tests
    @config should be a config object specifying the learning parameters
    """
    # Need to split actor & critic into different graphs/sessions to prevent serialization errors
    # See https://github.com/tflearn/tflearn/issues/381
    tfconfig = tf.ConfigProto()
    tfconfig.gpu_options.per_process_gpu_memory_fraction = 0.05


    with tf.Session(config=tfconfig) as sess:
        # Make the gym environment
        env = gym.make(config.ENVIRONMENT)
        env = wrappers.Monitor(env, os.path.join(config.SAVE_DIR, config.ENVIRONMENT+'-experiment'), force=True)

        # Set the tensorflow seed
        tf.set_random_seed(config.RANDOM_SEED)

        # Start training
        model = DDPG(sess, env, config)
        model.train()
        env.close()
