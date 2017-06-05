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

	# For random numbers
	seed = 1234

	# Max training steps
	max_episodes = 10000

	# Max episode length
	max_episode_length = 500

	# Base learning rate for the Actor network
	actor_learning_rate = 0.0001  # Paper uses 0.0001

	# Base learning rate for the Critic Network
	critic_learning_rate = 0.001  # Paper uses 0.001

	# L2 weight decay for Q
	l2_decay = 0.01  # Paper uses 0.01

	# Discount factor
	gamma = 0.99  # Paper uses 0.99

	# Soft target update param
	tau = 0.001  # Paper uses 0.001

	# Size of replay buffer
	buffer_size = 500

	# Training minibatch size
	batch_size = 64

	# Exploration parameters
	ou_mu = 0.0
	ou_theta = 0.15  # Paper uses 0.15
	ou_sigma = 0.20  # Paper uses 0.20
	tau2 = 25




class simulation(default):

	# Whether we should render the environment
	render = True

	# Where the model is loaded from
	load_dir = "weights/vision/"

	# Where the model is saved to
	save_dir = "weights/vision/"

	# Where to save the image
	image_path = "weights/vision/frame.jpg"

	# Use 1 to train the model and 0 to test
	learning_phase = 1

	# Exploration noise
	epsilon = 0.2

	# How often to save the model
	save_interval = 3
