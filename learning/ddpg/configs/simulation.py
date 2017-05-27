import os
from .default import config as base
from datetime import datetime


class config(base):

	ENVIRONMENT = 'CarSimulation'
	OUTPUT_RESULTS_DIR = os.pardir

	# Directory for storing TensorBoard summary results
	RANDOM_SEED = 1234

	# Set to restoring from file
	RESTORE_DATE = None

	# Where the model is saved
	SUMMARY_DIR = "weights/ddpg/simulated/"