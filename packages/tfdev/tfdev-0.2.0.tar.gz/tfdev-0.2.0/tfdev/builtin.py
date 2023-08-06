#!/usr/bin/env python3
import tensorflow as tf

from .collections import GlobalFeedDict

def weight_variable(shape, name):
    init_op = tf.truncated_normal(shape = shape, stddev = 0.1)
    return tf.get_variable(name = name, initializer = init_op)
    # return tf.Variable(tf.truncated_normal(shape = shape, stddev = 0.1), name = name)

def bias_variable(shape, name):
    init_op = tf.constant(0.1, shape = shape)
    return tf.get_variable(name = name, initializer = init_op)
    # return tf.Variable(tf.constant(0.1, shape = shape), name = name)

def batch_normalization(input_tensor, name = None):
    holder = GlobalFeedDict.share(name = GlobalFeedDict.const.BATCH_NORM, dtype = tf.bool, train_val = True, valid_val = False)
    return tf.layers.batch_normalization(
        input_tensor,
        axis = 1,
        fused = True,
        training = holder,
        name = name,
    )

def dropout(input_tensor, keep_prob):
    holder = GlobalFeedDict.add(dtype = tf.float32, train_val = keep_prob, valid_val = 1)
    h_dropout = tf.nn.dropout(input_tensor, keep_prob = holder)

    return h_dropout

def conv2d(input_tensor,
           filters,
           kernel_size,
           name,
           strides = (1, 1),
           act = None,
           data_format = 'NCHW',
           padding = 'SAME',
           weight_regularizer = None,
           bias_regularizer = None,
           output_regularizer = None,
           ):

    channels = None

    if data_format is 'NCHW':
        channels = int(input_tensor.get_shape()[1])
        strides = (1, 1) + tuple(strides)

    elif data_format is 'NHWC':
        channels = int(input_tensor.get_shape()[3])
        strides = (1, ) + tuple(strides) + (1, )

    else:
        raise ValueError('data_format should be either "NCHW" or "NHWC"')

    with tf.variable_scope(name):
        w = weight_variable(shape = tuple(kernel_size) + (channels, filters), name = 'Weight')
        b = bias_variable(shape = (filters, ), name = 'Bias')

    h_conv = tf.nn.conv2d(input_tensor, filter = w, strides = strides, padding = padding, data_format = data_format)
    h_conv_add_bias = tf.nn.bias_add(h_conv, b, data_format = data_format)

    if act is not None:
        h_conv_add_bias = act(h_conv_add_bias)

    if weight_regularizer:
        weight_regularizer.apply(w)

    if bias_regularizer:
        bias_regularizer.apply(b)

    if output_regularizer:
        output_regularizer.apply(h_conv_add_bias)

    return h_conv_add_bias

def dense(input_tensor,
          units,
          name,
          weight_regularizer = None,
          bias_regularizer = None,
          output_regularizer = None,
          act = None,
          ):

    input_dim = int(input_tensor.get_shape()[1])

    with tf.variable_scope(name):
        w = weight_variable((input_dim, units), name = 'Weight')
        b = bias_variable((units, ), name = 'Bias')

    h_dense = input_tensor @ w + b

    if act is not None:
        h_dense = act(h_dense)

    if weight_regularizer:
        weight_regularizer.apply(w)

    if bias_regularizer:
        bias_regularizer.apply(b)

    if output_regularizer:
        output_regularizer.apply(h_dense)

    return h_dense

def max_pool(input_tensor,
             kernel_size,
             strides = (1, 1),
             padding = 'SAME',
             data_format = 'NCHW',
             ):

    if data_format is 'NCHW':
        strides = (1, 1) + tuple(strides)
        kernel_size = (1, 1) + tuple(kernel_size)
    elif data_format is 'NHWC':
        strides = (1, ) + tuple(strides) + (1, )
        kernel_size = (1, ) + tuple(kernel_size) + (1, )
    else:
        raise ValueError('data_format should be either "NCHW" or "NHWC"')

    return tf.nn.max_pool(input_tensor, ksize = kernel_size, strides = strides, padding = padding, data_format = data_format)

def avg_pool(input_tensor,
             kernel_size,
             strides = (1, 1),
             padding = 'SAME',
             data_format = 'NCHW',
             ):

    if data_format is 'NCHW':
        strides = (1, 1) + tuple(strides)
    elif data_format is 'NHWC':
        strides = (1, ) + tuple(strides) + (1, )
    else:
        raise ValueError('data_format should be either "NCHW" or "NHWC"')

    return tf.nn.avg_pool(input_tensor, ksize = kernel_size, strides = strides, padding = padding, data_format = data_format)
