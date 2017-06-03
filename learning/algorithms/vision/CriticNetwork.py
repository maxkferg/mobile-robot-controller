import math
import numpy as np
import tensorflow as tf
import keras.backend as K
from keras.models import model_from_json, load_model
from keras.models import Sequential
from keras.layers import Dense, Flatten, Input, add, Lambda, Activation
from keras.models import Sequential, Model
from keras.initializers import *
from keras.optimizers import Adam
from .VisionNetwork import VisionNetwork

HIDDEN1_UNITS = 200
HIDDEN2_UNITS = 400

class CriticNetwork(object):
    def __init__(self, sess, config, state_size, action_size, BATCH_SIZE, TAU, LEARNING_RATE):
        self.sess = sess
        self.config = config
        self.BATCH_SIZE = BATCH_SIZE
        self.TAU = TAU
        self.LEARNING_RATE = LEARNING_RATE
        self.action_size = action_size

        K.set_session(sess)

        self.model, self.action, self.state = self.create_critic_network(state_size, action_size)
        self.target_model, self.target_action, self.target_state = self.create_critic_network(state_size, action_size)
        self.action_grads = tf.gradients(self.model.output, self.action)  #GRADIENTS for policy update
        self.sess.run(tf.global_variables_initializer())

    def gradients(self, states, actions):
        return self.sess.run(self.action_grads, feed_dict={
            self.state: states,
            self.action: actions
        })[0]

    def target_train(self):
        critic_weights = self.model.get_weights()
        critic_target_weights = self.target_model.get_weights()
        for i in range(len(critic_weights)):
            critic_target_weights[i] = self.TAU * critic_weights[i] + (1 - self.TAU)* critic_target_weights[i]
        self.target_model.set_weights(critic_target_weights)

    def create_critic_network(self, state_size, action_dim):
        """
        Create the critic network
        The network inputs are [sensors,frame,action]
        """
        vision = VisionNetwork(self.sess, self.config)
        action = Input(shape=[action_dim],name='action2')

        w1 = Dense(HIDDEN1_UNITS, activation='relu')(vision.output)
        a1 = Dense(HIDDEN2_UNITS, activation='linear')(action)
        h1 = Dense(HIDDEN2_UNITS, activation='linear')(w1)
        h2 = add([h1,a1])
        h3 = Dense(HIDDEN2_UNITS, activation='relu')(h2)
        V = Dense(action_dim, activation='linear')(h3)
        model = Model(inputs=[vision.input, action], outputs=V)
        adam = Adam(lr=self.LEARNING_RATE)
        model.compile(loss='mse', optimizer=adam)
        return model, action, vision.input
