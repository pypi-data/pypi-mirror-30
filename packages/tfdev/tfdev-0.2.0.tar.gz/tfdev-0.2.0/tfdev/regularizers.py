#!/usr/bin/env python3
import tensorflow as tf

from abc import ABC, abstractmethod
from tfdev.utils import Const

class Regularizer():

    keys = Const(
        REG = 'regularizer',
    )

    def __init__(self, c):
        self.__c = c

    @abstractmethod
    def __kernel__(self, matrix):
        pass

    def apply(self, matrix):
        tf.add_to_collection(Regularizer.keys.REG, self.__c * self.__kernel__(matrix))

class L1(Regularizer):

    def __kernel__(self, matrix):
        return tf.reduce_sum(abs(matrix))


class L2(Regularizer):

    def __kernel__(self, matrix):
        return tf.nn.l2_loss(matrix)

class L1L2(Regularizer):

    def __kernel__(self, matrix):
        return tf.nn.l2_loss(matrix) + tf.reduce_sum(abs(matrix))
