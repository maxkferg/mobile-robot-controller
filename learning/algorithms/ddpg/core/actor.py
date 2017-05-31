"""
DDPG Actor Network
"""
import numpy as np
import tensorflow as tf
import tflearn
import random
import os
import gym



class ActorNetwork(object):
    """
    Input to the network is the state, output is the action
    under a deterministic policy.

    The output layer activation is a tanh to keep the action
    between -action_bound and action_bound
    """
    def __init__(self, sess, state_dim, action_dim, action_bound, learning_rate, tau, restore=False, seed=0):
        self.sess = sess
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.action_bound = action_bound
        self.learning_rate = learning_rate
        self.tau = tau
        self.seed = seed

        self.is_training = tf.placeholder(tf.bool, name='Actor_is_training')

        if not restore:
            # Actor network
            self.inputs, self.outputs, self.scaled_outputs = self.create_actor_network()
            self.net_params = tf.trainable_variables()  # Returns a list of Variables where trainable=True

            # Target network
            self.target_inputs, self.target_outputs, self.target_scaled_outputs = self.create_actor_network("_target")
            self.target_net_params = tf.trainable_variables()[len(self.net_params):]

            # Temporary placeholder action gradient - this gradient will be provided by the critic network
            self.action_gradients = tf.placeholder(tf.float32, [None, self.action_dim], name="actor_action_gradient")

            # Combine dnetScaledOut/dnetParams with criticToActionGradient to get actorGradient
            self.actor_gradients = tf.gradients(self.scaled_outputs, self.net_params, -self.action_gradients,
                                                name="actor_gradient")

            self.optimize = tf.train.AdamOptimizer(self.learning_rate, name='Adam_Actor'). \
                apply_gradients(zip(self.actor_gradients, self.net_params))

            tf.add_to_collection('Actor_action_gradients', self.action_gradients)
            tf.add_to_collection('Actor_optimize', self.optimize)
        else:
            # Load Actor network
            self.inputs, self.out, self.scaled_outputs = self.load_actor_network()
            # Filter the loaded trainable variables for those belonging only to the actor network
            self.net_params = [v for v in tf.trainable_variables() if "actor" in v.name and "target" not in v.name]

            # Load Target network
            self.target_inputs, self.target_outputs, self.target_scaled_outputs = self.load_actor_network(True)
            # Filter the loaded trainable variables for those belonging only to the target actor network
            self.target_net_params = [v for v in tf.trainable_variables() if "actor" in v.name and "target" in v.name]

            self.action_gradients = tf.get_collection('Actor_action_gradients')[0]
            self.optimize = tf.get_collection('Actor_optimize')[0]

        # Op for periodically updating target network with online network weights
        self.update_target_net_params = \
            [self.target_net_params[i].assign(tf.multiply(self.net_params[i], self.tau) +
                                              tf.multiply(self.target_net_params[i], 1. - self.tau))
             for i in range(len(self.target_net_params))]

        self.num_trainable_vars = len(self.net_params) + len(self.target_net_params)


    def create_actor_network(self, suffix=""):
        state = tflearn.input_data(shape=[None, self.state_dim], name='actor_input'+suffix)
        # state_bn = tf.layers.batch_normalization(state, training=self.is_training, scale=False,
        #                                          name='actor_BN_input'+suffix)
        net = tflearn.fully_connected(state, 400, activation='tanh', name='actor_L1'+suffix,
                                      weights_init=tflearn.initializations.variance_scaling(seed=self.seed))
        if suffix == "":
            tf.summary.histogram("Actor/Layer1", net.W)
        # net = tf.layers.batch_normalization(net, training=self.is_training, scale=False,
        #                                     name='actor_BN1'+suffix)
        net = tflearn.fully_connected(net, 300, activation='tanh', name='actor_L2'+suffix,
                                      weights_init=tflearn.initializations.variance_scaling(seed=self.seed))
        if suffix == "":
            tf.summary.histogram("Actor/Layer2", net.W)
        # net = tf.layers.batch_normalization(net, training=self.is_training, scale=True,
        #                                     name='actor_BN2'+suffix)

        # Final layer weights are initialized to Uniform[-3e-3, 3e-3]
        weight_init_final = tflearn.initializations.uniform(minval=-0.003, maxval=0.003, seed=self.seed)
        action = tflearn.fully_connected(net, self.action_dim, activation='tanh', weights_init=weight_init_final,
                                         name='actor_output'+suffix)
        # Scale output to [-action_bound, action_bound]
        scaled_action = tf.multiply(action, self.action_bound, name='actor_output_scaled'+suffix)
        return state, action, scaled_action


    @staticmethod
    def load_actor_network(target=False):
        suffix = "_target" if target else ""
        inputs = tf.get_default_graph().get_tensor_by_name("actor_input"+suffix+"/X:0")
        out = tf.get_default_graph().get_tensor_by_name("actor_output"+suffix+"/Tanh:0")
        scaled_out = tf.get_default_graph().get_tensor_by_name("actor_output_scaled"+suffix+":0")
        return inputs, out, scaled_out


    def train(self, inputs, action_gradients):
        # Extra ops for BN. Parameters associated with the target network are ignored
        extra_update_ops = [v for v in tf.get_collection(tf.GraphKeys.UPDATE_OPS) if "actor" in v.name and "target" not in v.name]
        return self.sess.run([self.optimize, extra_update_ops],
                             feed_dict={self.inputs: inputs, self.action_gradients: action_gradients,
                                        self.is_training: True})


    def predict(self, inputs):
        return self.sess.run(self.scaled_outputs, feed_dict={self.inputs: inputs,
                                                             self.is_training: False})


    def predict_target(self, inputs):
        return self.sess.run(self.target_scaled_outputs, feed_dict={self.target_inputs: inputs,
                                                                    self.is_training: False})


    def update_target_network(self):
        self.sess.run(self.update_target_net_params, feed_dict={self.is_training: False})


    def get_num_trainable_vars(self):
        return self.num_trainable_vars