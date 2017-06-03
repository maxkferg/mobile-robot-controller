import json
import timeit
import random
import argparse
import numpy as np
import tensorflow as tf
from keras.models import model_from_json, Model
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.optimizers import Adam
from .ReplayBuffer import ReplayBuffer
from .ActorNetwork import ActorNetwork
from .CriticNetwork import CriticNetwork
from .OU import OU


OU = OU()       #Ornstein-Uhlenbeck Process

def vision_train(env, config, train_indicator=0):    #1 means Train, 0 means simply Run
    action_dim = 2  # Steering/Acceleration
    state_dim = 4  # Number of sensors input

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
    tfconfig.gpu_options.allow_growth = True
    sess = tf.Session(config=tfconfig)
    from keras import backend as K
    K.set_session(sess)

    actor = ActorNetwork(sess, config, state_dim, action_dim, config.batch_size, config.tau, config.actor_learning_rate)
    critic = CriticNetwork(sess, config, state_dim, action_dim, config.batch_size, config.tau, config.critic_learning_rate)
    buff = ReplayBuffer(config.buffer_size)    #Create replay buffer

    try:
        print("Trying to load weights from ",config.load_dir)
        actor_weights = os.path.join(config.save_dir,"actormodel.h5")
        critic_weights = os.path.join(config.save_dir,"actormodel.h5")
        actor.model.load_weights(actor_weights)
        critic.model.load_weights(critic_weights)
        actor.target_model.load_weights(actor_weights)
        critic.target_model.load_weights(critic_weights)
        print("Weights loaded successfully")
    except:
        print("Cannot weight files")

    print("Training...")
    for i in range(episode_count):

        print("Episode: {0}, Replay Buffer: {1}, Epsilon: {2}".format(i, buff.count(), epsilon))

        car = env.reset()
        s_t = car.frames

        total_reward = 0.
        for j in range(max_steps):
            loss = 0
            epsilon -= 1.0 / EXPLORE
            a_t = np.zeros([1,action_dim])
            noise_t = np.zeros([1,action_dim])

            # Reshape because there is only one item in the batch
            a_t_original = actor.model.predict(s_t[None,:])
            noise_t[0][0] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][0],  0.0 , 0.60, 0.30)
            noise_t[0][1] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][1],  0.5 , 1.00, 0.10)

            a_t[0][0] = a_t_original[0][0] + noise_t[0][0]
            a_t[0][1] = a_t_original[0][1] + noise_t[0][1]

            # Take a new sample from the environment
            car, r_t, done, info = env.step(a_t[0])

            # The camera frame becomes the state
            s_t1 = car.frames

            # Add to replay buffer
            buff.add((s_t, a_t[0], r_t, s_t1, done))     

            # Do the batch update
            batch = buff.getBatch(config.batch_size)
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

        if np.mod(i+1, config.save_interval) == 0:
            if (train_indicator):
                actor_weights = os.path.join(config.save_dir, "actormodel.h5")
                actor_json = os.path.join(config.save_dir, "actormodel.json")
                critic_weights = os.path.join(config.save_dir, "actormodel.h5")
                critic_json = os.path.join(config.save_dir, "criticmodel.json")

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

    env.end()  # This is for shutting down TORCS
    print("Finish.")

if __name__ == "__main__":
    playGame()
