#!/usr/bin/env python3
import numpy as np
import tensorflow as tf

from collections import namedtuple
from .utils import Const

_tuple_instance = namedtuple('holder', ['tensor', 'name', 'train', 'valid'])

class GlobalFeedDict():

    const = Const(BATCH_NORM = 'batchnorm')

    __tuples = []

    @classmethod
    def add(cls, dtype, train_val, valid_val):
        shape = np.array(train_val).shape

        tensor = tf.placeholder(dtype = dtype, shape = shape)
        GlobalFeedDict.__tuples.append(_tuple_instance(tensor = tensor, name = None, train = train_val, valid = valid_val))

        return tensor

    @classmethod
    def share(cls, name, dtype = None, train_val = None, valid_val = None):

        for t in GlobalFeedDict.__tuples:
            if t.name == name:
                return t.tensor

        shape = np.array(train_val).shape
        tensor = tf.placeholder(dtype = dtype, shape = shape)
        GlobalFeedDict.__tuples.append(_tuple_instance(tensor = tensor, name = name, train = train_val, valid = valid_val))

        return tensor

    @classmethod
    def get_feed_dict(cls, train = False):
        return { t.tensor: t.train if train else t.valid for t in GlobalFeedDict.__tuples }

class FeedDict():

    def __init__(self):

        self.__tuples = []

    def add(self, tensor, train, valid, name = None):

        self.__tuples.append(_tuple_instance(tensor = tensor, name = name, train = train, valid = valid))

    def get(self, name):
        for t in self.__tuples:
            if t.name == name:
                return t.tensor

        return None

    def get_feed_dict(self, train = False):
        return { t.tensor: t.train if train else t.valid for t in self.__tuples }
