import math
import numpy as np
import tensorflow as tf
import keras.backend as K
from keras.models import model_from_json
from keras.models import Sequential, Model
from keras.layers import Flatten, Input, Dropout
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.initializers import *
from keras.optimizers import Adam
from hardware.camera.interface import Camera


FILTERS1 = 2
FILTERS2 = 3
FILTERS3 = 4

class VisionNetwork(object):
    """
    Vision network that is used in both the actor and critic models
    The actor and critic do not share vision weights
    """
    def __init__(self,sess,config):
        K.set_session(sess)
        K.set_learning_phase(config.learning_phase) # for dropout

        layer0 = Input(shape=Camera.image_shape)
        layer1 = Convolution2D(FILTERS1, (8,8), strides=4, padding='same', activation='relu')(layer0)
        layer2 = MaxPooling2D(pool_size=(4,4))(layer1)
        layer3 = Dropout(0.2)(layer2)

        layer4 = Convolution2D(FILTERS2, (4,4), strides=2, padding='same', activation='relu')(layer3)
        layer5 = MaxPooling2D(pool_size=(2,2))(layer4)
        layer6 = Dropout(0.2)(layer5)

        layer7 = Convolution2D(FILTERS3, (3,3), padding='same', activation='relu')(layer6)
        layer8 = MaxPooling2D(pool_size=(2,2))(layer7)
        layer9 = Dropout(0.2)(layer8)

        self.output = Flatten()(layer9)
        self.input = layer0

        print("Vision Input: ",self.input._keras_shape)
        print("Vision Output: ",layer7._keras_shape)


