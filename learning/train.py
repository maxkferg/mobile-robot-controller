import argparse
import tensorflow as tf
from .environments.car import CarEnvironment
from .environments.test import TestEnvironment
from .q_learning.configs.linear import config
from .q_learning.schedule import LinearExploration, LinearSchedule
from .q_learning.linear import Linear


def train_car():
    env = CarEnvironment()
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



def train_simulation(draw=False, resume=False):
    # make env
    env = TestEnvironment(draw=draw)

    # exploration strategy
    exp_schedule = LinearExploration(env, config.eps_begin, config.eps_end, config.eps_nsteps)

    # learning rate schedule
    lr_schedule  = LinearSchedule(config.lr_begin, config.lr_end, config.lr_nsteps)

    # train
    model = Linear(env, config, resume=resume)
    model.run(exp_schedule, lr_schedule)



if __name__ == '__main__':
    parser = argparse.ArgumentParser("train.py")
    parser.add_argument("--draw", action='store_true', help="Draw the simulation?")
    parser.add_argument("--resume", action='store_true', help="Resume from file?")
    args = parser.parse_args()
    train_simulation(args.draw, args.resume)

