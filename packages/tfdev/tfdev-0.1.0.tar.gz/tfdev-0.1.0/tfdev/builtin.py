#!/usr/bin/env python3
import tensorflow as tf

from .collections import GlobalFeedDict

def weight_variable(shape, name = None):
    return tf.Variable(tf.truncated_normal(shape = shape, stddev = 0.1), name = name)

def bias_variable(shape, name = None):
    return tf.Variable(tf.constant(0.1, shape = shape), name = name)

def batch_norm(input_tensor, name = None):
    holder = GlobalFeedDict.share(name = GlobalFeedDict.const.BATCH_NORM, dtype = tf.bool, train_val = True, valid_val = False)
    return tf.layers.batch_normalization(
        input_tensor,
        axis = 1,
        fused = True,
        training = holder,
        name = name,
    )

def dropout_layer(input_tensor, keep_prob):
    holder = GlobalFeedDict.add(dtype = tf.float32, train_val = keep_prob, valid_val = 1)
    h_dropout = tf.nn.dropout(input_tensor, keep_prob = holder)

    return h_dropout

def conv(input_tensor,
         filters,
         filter_size,
         strides,
         batchnorm = False,
         dropout = None,
         act = tf.nn.relu,
         padding = 'SAME',
         name = None,
         ):

    h_conv = tf.layers.conv2d(input_tensor, filters = filters, kernel_size = filter_size, strides = strides, padding = padding, data_format = 'channels_first', name = name)

    if batchnorm:
        h_conv = batch_norm(h_conv, name = name + '/batchnorm' if name is not None else None)

    h_conv = act(h_conv)

    if dropout:
        return dropout_layer(h_conv, keep_prob = dropout)

    return h_conv

def dense(input_tensor,
          units,
          batchnorm = False,
          weight_regularizer = None,
          bias_regularizer = None,
          output_regularizer = None,
          dropout = None,
          act = tf.nn.relu,
          ):

    input_dim = int(input_tensor.get_shape()[1])
    w = weight_variable((input_dim, units))
    b = bias_variable((units, ))

    h_dense = input_tensor @ w + b

    if batchnorm:
        h_dense = batch_norm(h_dense)

    h_dense = act(h_dense)

    if dropout:
        h_dense = dropout_layer(h_dense, dropout)

    if weight_regularizer:
        weight_regularizer.apply(w)

    if bias_regularizer:
        bias_regularizer.apply(b)

    if output_regularizer:
        output_regularizer.apply(h_dense)

    return h_dense
