"""
Test the DDPG Network on a simple Gym environment
"""
import os
import gym
import tensorflow as tf
from gym import wrappers
from datetime import datetime
from core.ddpg import DDPG
from config.demo import config


if config.RESTORE_DATE is not None:
    config.SUMMARY_DIR = os.path.join(config.OUTPUT_RESULTS_DIR, 'results','ddpg' 'gym', config.ENVIRONMENT, config.RESTORE_DATE)
else:
    config.TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
    config.SUMMARY_DIR = os.path.join(config.OUTPUT_RESULTS_DIR, 'results','ddpg' 'gym', config.ENVIRONMENT, config.TIMESTAMP)



def main(_):
    # Need to split actor & critic into different graphs/sessions to prevent serialization errors
    # See https://github.com/tflearn/tflearn/issues/381
    tfconfig = tf.ConfigProto()
    tfconfig.gpu_options.per_process_gpu_memory_fraction = 0.05


    with tf.Session(config=tfconfig) as sess:
        # Make the gym environment
        env = gym.make(config.ENVIRONMENT)
        env = wrappers.Monitor(env, os.path.join(config.SUMMARY_DIR, config.ENVIRONMENT+'-experiment'), force=True)

        # Set the tensorflow seed
        tf.set_random_seed(config.RANDOM_SEED)

        # Start training
        model = DDPG(sess, env, config)
        model.train()
        env.close()

if __name__ == '__main__':
    tf.app.run()
