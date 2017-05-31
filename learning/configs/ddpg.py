import os
from time import strftime
from datetime import datetime


def timestamp():
	"""Return a directory suitable timestamp"""
	return strftime("%a-%H-%M")



class default:
	"""
	Default training parameters for any DDPG network
	"""
	# Max training steps
	MAX_EPISODES = 10000

	# Max episode length
	MAX_EP_STEPS = 2000

	# Base learning rate for the Actor network
	ACTOR_LEARNING_RATE = 0.0001  # Paper uses 0.0001

	# Base learning rate for the Critic Network
	CRITIC_LEARNING_RATE = 0.001  # Paper uses 0.001

	# L2 weight decay for Q
	L2_DECAY = 0.01  # Paper uses 0.01

	# Discount factor
	GAMMA = 0.99  # Paper uses 0.99

	# Soft target update param
	TAU = 0.001  # Paper uses 0.001

	# Size of replay buffer
	BUFFER_SIZE = 1000000
	MINIBATCH_SIZE = 64

	# Exploration parameters
	OU_MU = 0.0
	OU_THETA = 0.15  # Paper uses 0.15
	OU_SIGMA = 0.20  # Paper uses 0.20
	TAU2 = 25



class demo(default):

	ENVIRONMENT = 'SemisuperPendulumRandom-v0'
	OUTPUT_RESULTS_DIR = os.pardir

	# Directory for storing TensorBoard summary results
	RANDOM_SEED = 1234

	# Whether we should render the environment
	render = False

	# Where the model is loaded from
	LOAD_DIR = None#"weights/demo/Tue-19-20/"

	# Where the model is saved to
	SAVE_DIR = "weights/demo/{0}/".format(timestamp())

	# Soft target update param
	TAU = 0.001  # Paper uses 0.001



class simulation(default):

	ENVIRONMENT = 'CarSimulation'
	OUTPUT_RESULTS_DIR = os.pardir

	# Directory for storing TensorBoard summary results
	RANDOM_SEED = 1234

	# Whether we should render the environment
	render = False

	# Where the model is loaded from
	LOAD_DIR = None#"weights/ddpg/Tue-21-37/"#"weights/ddpg/Tue-20-28/"

	# Where the model is saved to
	SAVE_DIR = "weights/ddpg/{0}/".format(timestamp())

	# Soft target update param
	TAU = 0.001  # Paper uses 0.001

	# Exploration parameters
	OU_MU = 0.0
	OU_THETA = 0.45  # Paper uses 0.15
	OU_SIGMA = 0.60  # Paper uses 0.20
	TAU2 = 1000
