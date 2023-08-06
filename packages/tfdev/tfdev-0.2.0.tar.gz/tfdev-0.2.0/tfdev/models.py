#!/usr/bin/env python3
import tensorflow as tf

from abc import ABC, abstractmethod
from .collections import GlobalFeedDict
from .utils import Const

class Model(ABC):

    keys = Const(
        APP            = 'app',
        METRICS        = 'metrics',
        METRICS_UPDATE = 'metrics_update',
        OUTPUT         = 'output',
        TRAIN          = 'train',
    )

    def __init__(self, input_tensor, name = 'model', load_path = None):

        self.name = name

        self.__ops = {}
        self.__callbacks = []

        with tf.variable_scope(name):
            self.__ops[Model.keys.OUTPUT] = self.__build_model__(input_tensor)
            self.__ops[Model.keys.APP] = self.__ops[Model.keys.OUTPUT]

        self.__saver = tf.train.Saver()

        if load_path:
            self.__saver.restore(tf.get_default_session(), load_path)

    @abstractmethod
    def __build_model__(self, input_tensor):

        '''

        h_conv1 = tf.nn.conv(input_tensor, name = 'conv1', ...)
        h_conv2 = tf.nn.conv(h_conv2, name = 'conv2', ...)

        ...

        return h_dense @ w_output + b_output

        '''

        return tf.constant('Replace with a output tensor')

    def __run_dataset__(self, iter_op, dataset, train = False):

        dataset.init(train = train)

        while True:

            try:
                tf.get_default_session().run(iter_op, feed_dict = GlobalFeedDict.get_feed_dict(train = train))

            except tf.errors.OutOfRangeError:
                break

    def __enter__(self):
        return self

    def __exit__(self, type, msg, traceback):
        if type is not None:
            print(msg)

        tf.get_default_session().close()

        return False


    def compile(self,
                label_tensor,
                loss_op_func,
                metrics_op_func,
                lr = 1e-3,
                optimizer = tf.train.AdamOptimizer,
                callbacks = []
                ):

        self.__ops[Model.keys.METRICS], self.__ops[Model.keys.METRICS_UPDATE] = metrics_op_func(logits = self.__ops[Model.keys.OUTPUT], labels = label_tensor)
        self.__callbacks = callbacks

        loss = loss_op_func(logits = self.__ops[Model.keys.OUTPUT], labels = label_tensor)

        # Apply regularizer
        if len(tf.get_collection('regularizer')) > 0:
            loss += tf.add_n(tf.get_collection('regularizer'))

        # update_ops store moving average of batch normalization
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)

        if len(update_ops) == 0:
            self.__ops[Model.keys.TRAIN] = optimizer(learning_rate = lr).minimize(loss)

        else:
            # Apply batch normalization
            # Control dependency will run moving average before run optimizer
            with tf.control_dependencies(update_ops):
                self.__ops[Model.keys.TRAIN] = optimizer(learning_rate = lr).minimize(loss)

        # Execute callback: on_compile_end()
        for cb in self.__callbacks:
            cb.on_compile_end(self.__ops[Model.keys.METRICS])

        # Init variables
        tf.global_variables_initializer().run()

    def train(self, epochs, dataset):

        for i in range(1, epochs + 1):

            tf.local_variables_initializer().run()

            # Run optimizer
            self.__run_dataset__(
                iter_op = self.__ops[Model.keys.TRAIN],
                dataset = dataset,
                train = True,
            )

            # Run validation metric
            self.__run_dataset__(
                iter_op = self.__ops[Model.keys.METRICS_UPDATE],
                dataset = dataset,
                train = False,
            )

            metric = tf.get_default_session().run(self.__ops[Model.keys.METRICS])
            print('epochs: {0}, validation metrics: {1}'.format(i, metric))

            # Execute callback: on_epoch_end()
            # And check if keep training
            keep_train = True
            for cb in self.__callbacks:
                keep_train &= cb.on_epoch_end(i, self.__ops[Model.keys.METRICS], self)

            if not keep_train:
                return


    def close(self):
        tf.get_default_session().close()

    def save(self, path, step = None):
        self.__saver.save(sess = tf.get_default_session(), save_path = path, global_step = step)

    def load(self, path):
        self.__saver.restore(tf.get_default_session(), path)

    def rebuild(self, input_tensor):

        with tf.variable_scope(self.name, reuse = True):
            self.__ops[Model.keys.APP] = self.__build_model__(input_tensor)

    def predict(self, feed_dict):

        return self.__ops[Model.keys.APP].eval(feed_dict = { **feed_dict, **GlobalFeedDict.get_feed_dict(train = False) })
