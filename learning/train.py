import argparse
import tensorflow as tf
#from .environments.real import RealEnvironment
#from .environments.simulated import SimulatedEnvironment
from .sarsa.schedule import LinearExploration, LinearSchedule
from .sarsa.linear import Linear
from .ddpg import DDPG


def train_car_sarsa():
    """
    Train a q-learning agent using the simulation
    """
    from .sarsa.configs.linear import config
    env = RealEnvironment()
    config.eps_begin = 0
    config.eps_end = 0
    config.eps_nsteps = 0
    config.output_path  = "learning/results/q_learning/car/"
    config.model_output = config.output_path + "model.weights/"
    config.log_path     = config.output_path + "log.txt"
    config.plot_output  = config.output_path + "scores.png"
    config.nsteps_train = 100

    # exploration strategy
    exp_schedule = LinearExploration(env, config.eps_begin, config.eps_end, config.eps_nsteps)

    # learning rate schedule
    lr_schedule = LinearSchedule(config.lr_begin, config.lr_end, config.lr_nsteps)

    # train
    print("Training the CAR!")
    tf.reset_default_graph()
    model = Linear(env, config, resume=False)
    model.run(exp_schedule, lr_schedule)



def train_simulation_sarsa(draw=False, resume=False):
    """
    Train a q-learning agent using the simulation
    """
    from .q_learning.configs.linear import config

    env = SimulatedEnvironment(draw=draw)

    # exploration strategy
    exp_schedule = LinearExploration(env, config.eps_begin, config.eps_end, config.eps_nsteps)

    # learning rate schedule
    lr_schedule  = LinearSchedule(config.lr_begin, config.lr_end, config.lr_nsteps)

    # train
    model = Linear(env, config, resume=resume)
    model.run(exp_schedule, lr_schedule)



def train_simulation_ddpg(render=False, resume=False):
    """
    Train a ddpg agent using the simulation
    """
    from .environments.continuous import ContinuousEnvironment
    from .ddpg.configs.simulation import config

    env = ContinuousEnvironment(render=render)

    tfconfig = tf.ConfigProto()
    tfconfig.gpu_options.per_process_gpu_memory_fraction = 0.05

    with tf.Session(config=tfconfig) as sess:

        # Set the tensorflow seed
        tf.set_random_seed(config.RANDOM_SEED)

        # Start training
        model = DDPG(sess, env, config)
        model.train()
        env.close()



def train_car_ddpg(render=False, resume=False):
    """
    Train a ddpg agent using the simulation
    """
    from .environments.continuous import ContinuousEnvironment
    from .ddpg.configs.simulation import config

    env = ContinuousEnvironment(render=render)

    tfconfig = tf.ConfigProto()
    tfconfig.gpu_options.per_process_gpu_memory_fraction = 0.05

    with tf.Session(config=tfconfig) as sess:

        # Set the tensorflow seed
        tf.set_random_seed(config.RANDOM_SEED)

        # Start training
        model = DDPG(sess, env, config)
        model.train()
        env.close()
