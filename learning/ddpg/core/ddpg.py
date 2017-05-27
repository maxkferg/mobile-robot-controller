"""
Implementation of DDPG - Deep Deterministic Policy Gradient
Algorithm and hyperparameter details can be found here: http://arxiv.org/pdf/1509.02971v2.pdf
Variance scaling paper: https://arxiv.org/pdf/1502.01852v1.pdf
Thanks to GitHub users yanpanlau, pemami4911, songrotek and JunhongXu for their DDPG examples

Batch normalisation on the actor accelerates learning but has poor long term stability. Applying to the critic breaks
it, particularly on the state branch. Not sure why but I think this issue is specific to this environment 
"""
import os
import numpy as np
import tensorflow as tf
import tflearn
import random
import pickle
from time import time
from .replay import ReplayBuffer
from .actor import ActorNetwork
from .critic import CriticNetwork
from .noise import OUNoise



class DDPG:
    """
    DDPG Network

    Sufficiently general that it can be trained with any Gym environment
    """

    def __init__(self, sess, env, config):
        """
        Create the DDPG model object

        :param env: environment to be used for training
        :param actor: Actor network
        :param critic: Critic network
        :param saver: TensorFlow saver object
        :param replay_buffer: Replay buffer to store experience
        :return:
        """
        self.sess = sess
        self.env = env
        self.config = config

        state_dim = env.observation_space.shape[0]
        action_dim = env.action_space.shape[0]
        action_bound = env.action_space.high

        # Ensure action bound is symmetric
        assert (env.action_space.high == -env.action_space.low)

        # Restore networks and replay buffer from disk otherwise create new ones
        if config.RESTORE_DATE is not None:
            self.restore(config, self.env, directory=config.SUMMARY_DIR)
        else:
            self.actor = ActorNetwork(sess, state_dim, action_dim, action_bound, config.ACTOR_LEARNING_RATE, config.TAU, seed=config.RANDOM_SEED)
            self.critic = CriticNetwork(sess, state_dim, action_dim, config.CRITIC_LEARNING_RATE, config.L2_DECAY, config.TAU, seed=config.RANDOM_SEED)
            self.saver = tf.train.Saver()
            self.replay_buffer = ReplayBuffer(config.BUFFER_SIZE, config.RANDOM_SEED)



    def restore(self, directory):
        """
        Restore a model from a directory
        """
        config = self.config
        self.saver = tf.train.import_meta_graph(os.path.join(directory, "ddpg_model.meta"))
        self.saver.restore(sess, os.path.join(directory, "ddpg_model"))
        self.actor = ActorNetwork(sess, state_dim, action_dim, action_bound, config.ACTOR_LEARNING_RATE, config.TAU, restore=True, seed=config.RANDOM_SEED)
        self.critic = CriticNetwork(sess, state_dim, action_dim, config.CRITIC_LEARNING_RATE, config.TAU, restore=True, seed=config.RANDOM_SEED)

        # Initialize the uninitialized variables
        uninitialized_vars = []
        for var in tf.global_variables():
            try:
                self.sess.run(var)
            except tf.errors.FailedPreconditionError:
                uninitialized_vars.append(var)
        self.sess.run(tf.variables_initializer(uninitialized_vars))

        # Load the replay bufffer
        self.replay_buffer = pickle.load(open(os.path.join(directory, "replay_buffer.pkl"), "rb"))
        print("Model restored from %s" % os.path.join(directory, "ddpg_model"))



    def train(self):
        # Initialise variables
        config = self.config
        if config.RESTORE_DATE is None:
            self.sess.run(tf.global_variables_initializer())

        writer = tf.summary.FileWriter(config.SUMMARY_DIR, self.sess.graph)

        # Initialize target network weights & noise function
        self.actor.update_target_network()
        self.critic.update_target_network()

        for i in range(config.MAX_EPISODES):
            start = time()
            ep_rewards = []
            ep_q_rmse = []
            ep_action_dist = []
            ep_loss = []
            self.env.seed(config.RANDOM_SEED + i)
            s = self.env.reset()

            exploration_noise = OUNoise(self.actor.action_dim, config.OU_MU, config.OU_THETA, config.OU_SIGMA, config.RANDOM_SEED + i)

            for j in range(config.MAX_EP_STEPS):
                #if i > 100:
                self.env.render()

                a = self.actor.predict(np.reshape(s, (1, self.actor.state_dim)))  # Reshape state into a column

                # Add exploration noise
                if config.RESTORE_DATE is None:
                    epsilon = np.exp(-i/config.TAU2)
                    a += epsilon * exploration_noise.noise() / self.env.action_space.high
                else:
                    epsilon = 0

                # Step forward in the environment
                a = np.clip(a, self.env.action_space.low, self.env.action_space.high)
                s2, r, terminal, info = self.env.step(a[0])
                ep_action_dist.append(a[0])

                self.replay_buffer.add(np.reshape(s, (self.actor.state_dim,)),  # Previous state
                                       np.reshape(a, (self.actor.action_dim,)),  # Action
                                       r,  # Reward
                                       terminal,  # Terminal state (bool)
                                       np.reshape(s2, (self.actor.state_dim,)))  # New state

                # Keep adding experience to the memory until there are at least 50 episodes of samples before training
                if self.replay_buffer.size() > config.MINIBATCH_SIZE:
                    s_batch, a_batch, r_batch, t_batch, s2_batch = self.replay_buffer.sample_batch(config.MINIBATCH_SIZE)

                    # Calculate target q
                    target_q = self.critic.predict_target(s2_batch, self.actor.predict_target(s2_batch))
                    ep_q_rmse.append(np.sqrt(np.mean((target_q - r_batch) ** 2, axis=0)))
                    y = r_batch + config.GAMMA * target_q * ~t_batch

                    # Update the critic given the targets
                    _, loss = self.critic.train(s_batch, a_batch, y)

                    # Update the actor policy using the sampled gradient
                    a_outs = self.actor.predict(s_batch)
                    grads = self.critic.action_gradients(s_batch, a_outs)
                    # grads = np.clip(grads, -1, 1)  # Gradient clipping to prevent exploding gradients
                    self.actor.train(s_batch, grads[0])

                    # Update target networks
                    self.actor.update_target_network()
                    self.critic.update_target_network()
                else:
                    loss = 0

                s = s2  # new state is the output from this step
                ep_rewards.append(r)
                ep_loss.append(loss)

                if terminal or j == config.MAX_EP_STEPS - 1:
                    # Add results to summaries
                    episode_summary = tf.Summary()
                    episode_summary.value.add(tag="Reward", simple_value=np.sum(ep_rewards))
                    episode_summary.value.add(tag="Q_RMSE", simple_value=np.mean(ep_q_rmse))
                    episode_summary.value.add(tag="Epsilon", simple_value=epsilon)
                    episode_summary.value.add(tag="Loss", simple_value=loss)

                    self.add_histogram(writer, "Actions", np.ravel(ep_action_dist), i)
                    self.add_histogram(writer, "Rewards", np.array(ep_rewards), i)

                    summary_str = self.sess.run(tf.summary.merge_all())
                    writer.add_summary(episode_summary, i)
                    writer.add_summary(summary_str, i)
                    writer.flush()
                    print('Reward: %.2f' % np.sum(ep_rewards), '\t Episode', i,
                          '\tQ RMSE: %.2f' % np.mean(ep_q_rmse),
                          '\tTime: %.1f' % (time() - start),
                          '\tEpsilon: %.3f' % epsilon,
                          '\tLoss: %.3f' % np.mean(ep_loss)),
                    exploration_noise.reset()
                    break

            # Save model every 50 steps
            if i % 50 == 0 and i != 0:
                save_start = time()
                save_model = os.path.join(config.SUMMARY_DIR, "ddpg_model")
                save_buffer = os.path.join(config.SUMMARY_DIR, "replay_buffer.pkl")
                save_path = self.saver.save(self.sess, config.SUMMARY_DIR)
                pickle.dump(self.replay_buffer, open(save_buffer, "wb"))
                print("Model saved in %.1f" % (time() - save_start), "seconds. Path: %s" % save_path)



    def add_histogram(self, writer, tag, values, step, bins=1000):
        """
        Logs the histogram of a list/vector of values.
        """
        counts, bin_edges = np.histogram(values, bins=bins)

        # Fill fields of histogram proto
        hist = tf.HistogramProto()
        hist.min = float(np.min(values))
        hist.max = float(np.max(values))
        hist.num = int(np.prod(values.shape))
        hist.sum = float(np.sum(values))
        hist.sum_squares = float(np.sum(values ** 2))

        # Requires equal number as bins, where the first goes from -DBL_MAX to bin_edges[1]
        # See https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/framework/summary.proto#L30
        # Thus, we drop the start of the first bin
        bin_edges = bin_edges[1:]

        # Add bin edges and counts
        for edge in bin_edges:
            hist.bucket_limit.append(edge)
        for c in counts:
            hist.bucket.append(c)

        # Create and write Summary
        summary = tf.Summary(value=[tf.Summary.Value(tag=tag, histo=hist)])
        writer.add_summary(summary, step)


