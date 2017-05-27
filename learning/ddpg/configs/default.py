

class config:
	"""
	Default training parameters for any DDPG network
	"""
	# Max training steps
	MAX_EPISODES = 1000

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
