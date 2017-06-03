import tensorflow as tf
import tensorflow.contrib.layers as layers
from builtins import zip
from builtins import range
from .utils.general import get_logger
from .utils.test_env import EnvTest
from .core.deep_q_learning import DQN
from .schedule import LinearExploration, LinearSchedule



class QNetwork(DQN):
    """
    Implement Fully Connected with Tensorflow
    """

    def __init__(self, env, config, resume=False, logger=None):
        """
        Initialize the exploration schedule and the learning rate schedule
        """
        #self.config = config
        self.exp_schedule = LinearExploration(env, config.eps_begin, config.eps_end, config.eps_nsteps)
        self.lr_schedule  = LinearSchedule(config.lr_begin, config.lr_end, config.lr_nsteps)
        super().__init__(env, config, resume, logger)


    def add_placeholders_op(self):
        """
        Adds placeholders to the graph

        These placeholders are used as inputs by the rest of the model building and will be fed
        data during training.  Note that when "None" is in a placeholder's shape, it's flexible
        (so we can use different batch sizes without rebuilding the model
        """
        # this information might be useful
        # here, typically, a state shape is (80, 80, 1)
        state_shape = list(self.env.observation_space.shape)

        ##############################################################
        """
        TODO: add placeholders:
              Remember that we stack 4 consecutive frames together, ending up with an input of shape
              (80, 80, 4).
               - self.s: batch of states, type = uint8
                         shape = (batch_size, img height, img width, nchannels x config.state_history)
               - self.a: batch of actions, type = int32
                         shape = (batch_size)
               - self.r: batch of rewards, type = float32
                         shape = (batch_size)
               - self.sp: batch of next states, type = uint8
                         shape = (batch_size, img height, img width, nchannels x config.state_history)
               - self.done_mask: batch of done, type = bool
                         shape = (batch_size)
                         note that this placeholder contains bool = True only if we are done in
                         the relevant transition
               - self.lr: learning rate, type = float32

        (Don't change the variable names!)

        HINT: variables from config are accessible with self.config.variable_name
              Also, you may want to use a dynamic dimension for the batch dimension.
              Check the use of None for tensorflow placeholders.

              you can also use the state_shape computed above.
        """
        img_height = state_shape[0]
        img_width = state_shape[1]
        #nchannels = state_shape[2]

        s_shape = (None, img_height, img_width, self.config.state_history)
        a_shape = (None,)
        r_shape = (None,)
        sp_shape = (None, img_height, img_width, self.config.state_history)
        done_mask_shape = (None,)
        lr_shape = ()

        self.s = tf.placeholder(tf.uint8, s_shape)
        self.a = tf.placeholder(tf.int32, a_shape)
        self.r = tf.placeholder(tf.float32, r_shape)
        self.sp = tf.placeholder(tf.uint8, sp_shape)
        self.done_mask = tf.placeholder(tf.bool, done_mask_shape)
        self.lr = tf.placeholder(tf.float32, lr_shape)


    def get_q_values_op(self, state, scope, reuse=False):
        """
        Returns Q values for all actions

        Args:
            state: (tf tensor)
                shape = (batch_size, img height, img width, nchannels)
            scope: (string) scope name, that specifies if target network or not
            reuse: (bool) reuse of variables in the scope

        Returns:
            out: (tf tensor) of shape = (batch_size, num_actions)
        """
        # this information might be useful
        num_actions = self.env.action_space.n
        """
        TODO: implement a fully connected with no hidden layer (linear
            approximation) using tensorflow. In other words, if your state s
            has a flattened shape of n, and you have m actions, the result of
            your computation sould be equal to
                W s where W is a matrix of shape m x n

        HINT: you may find tensorflow.contrib.layers useful (imported)
              make sure to understand the use of the scope param

              you can use any other methods from tensorflow
              you are not allowed to import extra packages (like keras,
              lasagne, cafe, etc.)
        """
        with tf.variable_scope(scope, reuse=reuse):
            state = layers.flatten(state)
            hidden = layers.fully_connected(
                inputs=state,
                num_outputs=self.config.n_hidden_layers,
                activation_fn=tf.nn.relu, # linear
                trainable=True
            )

            out = layers.fully_connected(
                inputs=hidden,
                num_outputs=num_actions,
                activation_fn=None, # linear
                trainable=True
            )
        return out


    def add_update_target_op(self, q_scope, target_q_scope):
        """
        update_target_op will be called periodically
        to copy Q network weights to target Q network

        Remember that in DQN, we maintain two identical Q networks with
        2 different set of weights. In tensorflow, we distinguish them
        with two different scopes. One for the target network, one for the
        regular network. If you're not familiar with the scope mechanism
        in tensorflow, read the docs
        https://www.tensorflow.org/programmers_guide/variable_scope

        Periodically, we need to update all the weights of the Q network
        and assign them with the values from the regular network. Thus,
        what we need to do is to build a tf op, that, when called, will
        assign all variables in the target network scope with the values of
        the corresponding variables of the regular network scope.

        Args:
            q_scope: (string) name of the scope of variables for q
            target_q_scope: (string) name of the scope of variables
                        for the target network
        """
        ##############################################################
        """
        TODO: add an operator self.update_target_op that assigns variables
            from target_q_scope with the values of the corresponding var
            in q_scope

        HINT: you may find the following functions useful:
            - tf.get_collection
            - tf.assign
            - tf.group

        """
        Q = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=q_scope)
        Qt = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=target_q_scope)
        ops = [tf.assign(Qt[i],Q[i]) for i in range(len(Q))]
        self.update_target_op = tf.group(*ops)


    def add_loss_op(self, q, target_q):
        """
        Sets the loss of a batch, self.loss is a scalar

        Args:
            q: (tf tensor) shape = (batch_size, num_actions)
            target_q: (tf tensor) shape = (batch_size, num_actions)
        """
        # you may need this variable
        num_actions = self.env.action_space.n
        not_done = 1-tf.cast(self.done_mask, tf.float32)
        indices = tf.one_hot(self.a, num_actions)
        q_samp = self.r + not_done*self.config.gamma*tf.reduce_max(target_q, axis=1)
        q_sa = tf.reduce_sum(q * indices, axis=1)
        self.loss = tf.reduce_mean((q_samp - q_sa)**2)


    def add_optimizer_op(self, scope):
        """
        Set self.train_op and self.grad_norm
        """
        optimizer = tf.train.AdamOptimizer(learning_rate=self.lr)
        variables = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=scope)
        gradients, v = list(zip(*optimizer.compute_gradients(self.loss, variables)))

        if self.config.grad_clip:
            gradients,_ = tf.clip_by_global_norm(gradients, self.config.clip_val)

        # Use the clipped gradients for optimization
        self.grad_norm = tf.global_norm(gradients)
        self.train_op = optimizer.apply_gradients(list(zip(gradients, v)))
