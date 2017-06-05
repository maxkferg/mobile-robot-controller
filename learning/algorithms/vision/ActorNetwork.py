import math
import numpy as np
import tensorflow as tf
import keras.backend as K
from keras.models import model_from_json
from keras.models import Sequential, Model
from keras.layers import Dense, Flatten, Input, concatenate, Lambda
from keras.initializers import *
from keras.optimizers import Adam
from .VisionNetwork import VisionNetwork

HIDDEN1_UNITS = 10
HIDDEN2_UNITS = 20

class ActorNetwork(object):
    def __init__(self, sess, config, state_size, action_size, BATCH_SIZE, TAU, LEARNING_RATE):
        self.sess = sess
        self.config = config
        self.BATCH_SIZE = BATCH_SIZE
        self.TAU = TAU
        self.LEARNING_RATE = LEARNING_RATE

        K.set_session(sess)

        self.model , self.weights, self.state = self.create_actor_network(state_size, action_size)
        self.target_model, self.target_weights, self.target_state = self.create_actor_network(state_size, action_size)
        self.action_gradient = tf.placeholder(tf.float32,[None, action_size])
        self.params_grad = tf.gradients(self.model.output, self.weights, -self.action_gradient)
        grads = zip(self.params_grad, self.weights)
        self.optimize = tf.train.AdamOptimizer(LEARNING_RATE).apply_gradients(grads)
        self.sess.run(tf.global_variables_initializer())

    def train(self, states, action_grads):
        self.sess.run(self.optimize, feed_dict={
            self.state: states,
            self.action_gradient: action_grads
        })

    def target_train(self):
        actor_weights = self.model.get_weights()
        actor_target_weights = self.target_model.get_weights()
        for i in range(len(actor_weights)):
            actor_target_weights[i] = self.TAU * actor_weights[i] + (1 - self.TAU)* actor_target_weights[i]
        self.target_model.set_weights(actor_target_weights)


    def create_actor_network(self, state_size, action_dim):
        """Return the actor as a (input,output) tuple"""
        # Build the vision network
        vision = VisionNetwork(self.sess, self.config)
        hidden0 = Dense(HIDDEN1_UNITS, activation='relu')(vision.output)
        hidden1 = Dense(HIDDEN2_UNITS, activation='relu')(hidden0)
        # We use tanh nonlinearities because the output space should be between 0 and 1
        steering = Dense(1,activation='tanh', kernel_initializer=TruncatedNormal(mean=0.0, stddev=0.05, seed=None))(hidden1)
        throttle = Dense(1,activation='tanh', kernel_initializer=TruncatedNormal(mean=0.0, stddev=0.05, seed=None))(hidden1)
        controls = concatenate([steering, throttle])
        model = Model(inputs=vision.input, outputs=controls)
        return model, model.trainable_weights, vision.input
