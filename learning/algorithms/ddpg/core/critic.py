"""
DDPG Critic Network
"""
import numpy as np
import tensorflow as tf
import tflearn
import random
import os
import gym


class CriticNetwork(object):
    """
    Input to the network is the state and action, output is Q(s,a).
    The action must be obtained from the output of the Actor network.
    """
    def __init__(self, sess, state_dim, action_dim, learning_rate, l2_decay, tau, restore=False, seed=0):
        self.sess = sess
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.l2_decay = l2_decay
        self.tau = tau
        self.seed = seed

        self.is_training = tf.placeholder(tf.bool, name='Critic_is_training')

        if not restore:
            # Create the Critic network
            self.inputs, self.action, self.outputs = self.create_critic_network()
            self.network_params = [v for v in tf.trainable_variables() if "critic" in v.name]

            # Create the Target Network
            self.target_inputs, self.target_action, self.target_outputs = self.create_critic_network("_target")
            self.target_network_params = [v for v in tf.trainable_variables() if
                                          "critic" in v.name and "target" in v.name]

            # Network target (y_i) - Obtained from the target networks
            self.q_value = tf.placeholder(tf.float32, [None, self.action_dim], name="critic_q_value")
            self.L2 = tf.add_n([self.l2_decay * tf.nn.l2_loss(v) for v in self.network_params if "/W" in v.name])
            self.loss = tf.losses.mean_squared_error(self.q_value, self.outputs) + self.L2
            self.optimize = tf.train.AdamOptimizer(self.learning_rate, name='Adam_Critic').minimize(self.loss)

            tf.add_to_collection('Critic_q_value', self.q_value)
            tf.add_to_collection('Critic_loss', self.loss)
            tf.add_to_collection('Critic_optimize', self.optimize)

        else:
            # Load the Critic network
            self.inputs, self.action, self.outputs = self.load_critic_network()
            # Filter the loaded trainable variables for those belonging only to the critic network
            self.network_params = [v for v in tf.trainable_variables() if "critic" in v.name and "target" not in v.name]

            # Load the Target Network
            self.target_inputs, self.target_action, self.target_outputs = self.load_critic_network(True)
            # Filter the loaded trainable variables for those belonging only to the target critic network
            self.target_network_params = [v for v in tf.trainable_variables() if
                                          "critic" in v.name and "target" in v.name]

            self.q_value = tf.get_collection('Critic_q_value')[0]
            self.L2 = tf.add_n([self.l2_decay * tf.nn.l2_loss(v) for v in self.network_params if "/W" in v.name])
            self.loss = tf.get_collection('Critic_loss')[0] + self.L2
            self.optimize = tf.get_collection('Critic_optimize')[0]

        # Op for periodically updating target network with online network weights
        self.update_target_net_params = \
            [self.target_network_params[i].assign(tf.multiply(self.network_params[i], self.tau) +
                                                  tf.multiply(self.target_network_params[i], 1. - self.tau))
             for i in range(len(self.target_network_params))]

        # Get the gradient of the critic w.r.t. the action
        self.action_grads = tf.gradients(self.outputs, self.action, name="critic_action_gradient")
        tf.summary.scalar("L2", self.L2)

    def create_critic_network(self, suffix=""):
        # Critic breaks when BN is added to the state in Pendulum-v0. Not sure why :(
        state = tflearn.input_data(shape=[None, self.state_dim], name="critic_input_state"+suffix)
        # state_bn = tf.layers.batch_normalization(state, training=self.is_training, scale=False,
        #                                          name='critic_BN_input'+suffix)
        action = tflearn.input_data(shape=[None, self.action_dim], name="critic_input_action"+suffix)
        # action_bn = tf.layers.batch_normalization(action, training=self.is_training, scale=False,
        #                                           name='critic_BN_action'+suffix)
        net = tflearn.fully_connected(state, 400, activation='tanh', name='critic_L1'+suffix,
                                      weights_init=tflearn.initializations.variance_scaling(seed=self.seed))
        if suffix == "":
            tf.summary.histogram("Critic/Layer1", net.W)
        # net = tf.layers.batch_normalization(net, training=self.is_training, scale=False,
        #                                     name='critic_BN1'+suffix)
        # Add the action tensor in the 2nd hidden layer and create variables for W's and b
        s_union = tflearn.fully_connected(net, 300, name="critic_L2_state" + suffix,
                                          weights_init=tflearn.initializations.variance_scaling(seed=self.seed))
        a_union = tflearn.fully_connected(action, 300, name="critic_L2_action" + suffix,
                                          weights_init=tflearn.initializations.variance_scaling(seed=self.seed))
        net = tf.nn.tanh(tf.matmul(net, s_union.W) + tf.matmul(action, a_union.W) + s_union.b,
                         name='critic_L2' + suffix)
        if suffix == "":
            tf.summary.histogram("Critic/Layer2/state", s_union.W)
            tf.summary.histogram("Critic/Layer2/action", a_union.W)

        # Linear layer connected to action_dim outputs representing Q(s,a). Weights are init to Uniform[-3e-3, 3e-3]
        weight_init = tflearn.initializations.uniform(minval=-0.003, maxval=0.003, seed=self.seed)
        q_value = tflearn.fully_connected(net, self.action_dim, activation="linear",
                                          weights_init=weight_init, name='critic_output'+suffix)
        return state, action, q_value

    @staticmethod
    def load_critic_network(target=False):
        suffix = "_target" if target else ""
        inputs = tf.get_default_graph().get_tensor_by_name("critic_input_state"+suffix+"/X:0")
        action = tf.get_default_graph().get_tensor_by_name("critic_input_action"+suffix+"/X:0")
        out = tf.get_default_graph().get_tensor_by_name("critic_output"+suffix+"/BiasAdd:0")
        return inputs, action, out

    def train(self, inputs, action, target_q_value):
        # Extra ops for BN. Parameters associated with the target network are ignored
        extra_update_ops = [v for v in tf.get_collection(tf.GraphKeys.UPDATE_OPS) if
                            "critic" in v.name and "target" not in v.name]
        return self.sess.run([self.optimize, self.loss, extra_update_ops], feed_dict={
            self.inputs: inputs,
            self.action: action,
            self.q_value: target_q_value,
            self.is_training: True
        })[:2]

    def predict(self, inputs, action):
        return self.sess.run(self.outputs, feed_dict={self.inputs: inputs, self.action: action,
                                                      self.is_training: False})

    def predict_target(self, inputs, action):
        return self.sess.run(self.target_outputs, feed_dict={self.target_inputs: inputs, self.target_action: action,
                                                             self.is_training: False})

    def action_gradients(self, inputs, action):
        return self.sess.run(self.action_grads, feed_dict={self.inputs: inputs, self.action: action,
                                                           self.is_training: False})

    def update_target_network(self):
        self.sess.run(self.update_target_net_params, feed_dict={self.is_training: False})
