import os
import random
import argparse
import numpy as np
from keras.models import model_from_json, Model
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.optimizers import Adam
import tensorflow as tf
import json

from ReplayBuffer import ReplayBuffer
from ActorNetwork import ActorNetwork
from CriticNetwork import CriticNetwork
from OU import OU
import timeit

OU = OU()       #Ornstein-Uhlenbeck Process

def train(train_indicator=0, env, config):    #1 means Train, 0 means simply Run
    action_dim = 2  # Steering/Acceleration
    state_dim = 20  # Number of sensors
    np.random.seed(1337)
    EXPLORE = 100000.
    episode_count = 2000
    max_steps = 100000
    reward = 0
    done = False
    step = 0
    epsilon = 1
    indicator = 0

    # Tensorflow GPU optimization
    tfconfig = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=tfconfig)
    from keras import backend as K
    K.set_session(sess)

    actor = ActorNetwork(sess, state_dim, action_dim, config.batch_size, config.tau, config.actor_learning_rate)
    critic = CriticNetwork(sess, state_dim, action_dim, config.batch_size, config.tau, config.critic_learning_rate)
    buff = ReplayBuffer(config.buffer_size)    #Create replay buffer

    #Now load the weight
    print("Load the weights")
    try:
        actor_weights = os.path.join(config.load_dir,"actormodel.h5")
        critic_weights = os.path.join(config.load_dir,,"criticmodel.h5")
        actor.model.load_weights(actor_weights)
        critic.model.load_weights(critic_weights)
        actor.target_model.load_weights(actor_weights)
        critic.target_model.load_weights(critic_weights)
        print("Weights loaded successfully")
    except:
        print("Cannot find the weights")

    print("Training...")
    for i in range(episode_count):

        print("Episode: {0} Replay Buffer: {1} Epsilon:{2:.2f}".format(i, buff.count(), epsilon))

        car = env.reset()
        total_reward = 0.

        for j in range(max_steps):
            loss = 0
            epsilon -= 1.0 / EXPLORE
            a_t = np.zeros([1,action_dim])
            noise_t = np.zeros([1,action_dim])

            a_t_original = actor.model.predict([car.sensors, car.frame])
            noise_t[0][0] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][0],  0.0 , 0.60, 0.30)
            noise_t[0][1] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][1],  0.5 , 1.00, 0.10)
            noise_t[0][2] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][2], -0.1 , 1.00, 0.05)

            #The following code do the stochastic brake
            #if random.random() <= 0.1:
            #    print("********Now we apply the brake***********")
            #    noise_t[0][2] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][2],  0.2 , 1.00, 0.10)

            a_t[0][0] = a_t_original[0][0] + noise_t[0][0]
            a_t[0][1] = a_t_original[0][1] + noise_t[0][1]

            car, r_t, done, info = env.step(a_t[0])

            buff.add(car, a_t[0], r_t, s_t1, done)      # Add replay buffer

            # Do the batch update
            batch = buff.getBatch(BATCH_SIZE)
            states = np.asarray([e[0] for e in batch])
            actions = np.asarray([e[1] for e in batch])
            rewards = np.asarray([e[2] for e in batch])
            new_states = np.asarray([e[3] for e in batch])
            dones = np.asarray([e[4] for e in batch])
            y_t = np.asarray([e[1] for e in batch])

            target_q_values = critic.target_model.predict([new_states, actor.target_model.predict(new_states)])

            for k in range(len(batch)):
                if dones[k]:
                    y_t[k] = rewards[k]
                else:
                    y_t[k] = rewards[k] + config.gamma*target_q_values[k]

            if (train_indicator):
                loss += critic.model.train_on_batch([states,actions], y_t)
                a_for_grad = actor.model.predict(states)
                grads = critic.gradients(states, a_for_grad)
                actor.train(states, grads)
                actor.target_train()
                critic.target_train()

            total_reward += r_t
            s_t = s_t1

            print("Episode", i, "Step", step, "Action", a_t, "Reward", r_t, "Loss", loss)

            step += 1
            if done:
                break

        if np.mod(i, 3) == 0:
            if (train_indicator):
                actor_weights = os.path.join(config.save_dir,"actormodel.h5")
                actor_json = os.path.join(config.save_dir,"actormodel.json")
                critic_weights = os.path.join(config.save_dir,"actormodel.h5")
                critic_json = os.path.join(config.save_dir,,"criticmodel.json")

                actor.model.save_weights(actor_weights, overwrite=True)
                with open(actor_json, "w") as outfile:
                    json.dump(actor.model.to_json(), outfile)

                critic.model.save_weights(critic_weights, overwrite=True)
                with open(critic_json, "w") as outfile:
                    json.dump(critic.model.to_json(), outfile)
                print("Saved weights to {0}".format(config.save_dir))

        print("TOTAL REWARD @ " + str(i) +"-th Episode  : Reward " + str(total_reward))
        print("Total Step: " + str(step))
        print("")

    env.end()
    print("Finished.")

if __name__ == "__main__":
    playGame()
