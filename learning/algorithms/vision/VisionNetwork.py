import numpy as np
import math
from keras.models import model_from_json
from keras.models import Sequential, Model
from keras.layers import Dense, Flatten, Input, concatenate, Lambda
from keras.initializers import *
from keras.optimizers import Adam
import tensorflow as tf
import keras.backend as K

IMAGE_SHAPE = (360, 640, 3)

class VisionNetwork(object):
    """
    Vision network that is used in both the actor and critic models
    The actor and critic do not share vision weights
    """
    def __init__(self):
        layer0 = Input(shape=[IMAGE_SHAPE])
        layer1 = Convolution2D(32, 3, 3, border_mode='same', activation='relu')(layer0)
        layer2 = Convolution2D(32, 3, 3, activation='relu')(layer1)
        layer3 = MaxPooling2D(pool_size=(2, 2))(layer2)
        layer4 = Dropout(0.2)(layer4)

        layer5 = Convolution2D(64, 3, 3, border_mode='same', activation='relu')(layer4)
        layer6 = Convolution2D(64, 3, 3, activation='relu')(layer5)
        layer7 = MaxPooling2D(pool_size=(2, 2))(layer6)
        layer8 = Dropout(0.2)(layer7)

        layer9 =Convolution2D(128, 3, 3, border_mode='same', activation='relu')(layer8)
        layer10 = Convolution2D(128, 3, 3, activation='relu')(layer9)
        layer11 = MaxPooling2D(pool_size=(2, 2))(layer10)
        layer12 = Dropout(0.2)(layer11)

        self.output = Flatten()(layer12)
        self.input = layer0