#!/usr/bin/env python3
import tensorflow as tf

from abc import ABC
from .collections import FeedDict

class Dataset(ABC):

    def __init__(self, batch_size, validation_batch_size, shuffle):

        self._feed_dict = FeedDict()
        self._iterator = None

        self._feed_dict.add(
            tensor = tf.placeholder(tf.int64),
            name = 'shuffle',
            train = shuffle,
            valid = 1,
        )

        self._feed_dict.add(
            tensor = tf.placeholder(tf.int64),
            name = 'batch_size',
            train = batch_size,
            valid = validation_batch_size,
        )

    @property
    def initializer(self):
        if self._iterator is None:
            self._iterator = self.__pipeline__().make_initializable_iterator()

        return self._iterator.initializer

    @property
    def next_batch(self):
        if self._iterator is None:
            self._iterator = self.__pipeline__().make_initializable_iterator()

        return self._iterator.get_next()

    def __pipeline__(self):
        return tf.data.Dataset()

    def get_feed_dict(self, train = False):
        return self._feed_dict.get_feed_dict(train = train)

    def init(self, train):
        self.initializer.run(feed_dict = self.get_feed_dict(train = train))

class TFRecordDataset(Dataset):

    def __init__(self, train_data, validation_data, parse_fn, parallel_call = 1, *args, **kargs):

        super(TFRecordDataset, self).__init__(*args, **kargs)

        self._feed_dict.add(
            tensor = tf.placeholder(tf.string, shape = [None]),
            name = 'data',
            train = train_data,
            valid = validation_data,
        )

        self.parse_fn = parse_fn
        self.parallel_call = parallel_call

    def __parse_tfrecord__(self, example_proto):
        return example_proto

    def __pipeline__(self):

        dataset = tf.data.TFRecordDataset(self._feed_dict.get('data')) \
                    .map(self.parse_fn, num_parallel_calls = self.parallel_call) \
                    .shuffle(buffer_size = self._feed_dict.get('shuffle')) \
                    .batch(self._feed_dict.get('batch_size'))

        return dataset

class NumpyDataset(Dataset):

    def __init__(self, x_train, y_train, x_validation = None, y_validation = None, *args, **kargs):

        if x_train.dtype != x_validation.dtype or y_train.dtype != y_validation.dtype:
            raise TypeError('train_data and validation_data should have the same data type of numpy')

        super(NumpyDataset, self).__init__(*args, **kargs)

        self._feed_dict.add(
            tensor = tf.placeholder(x_train.dtype, shape = (None,) + x_train.shape[1:]),
            name = 'features',
            train = x_train,
            valid = x_validation,
        )

        self._feed_dict.add(
            tensor = tf.placeholder(y_train.dtype, shape = (None,) + y_train.shape[1:]),
            name = 'labels',
            train = y_train,
            valid = y_validation,
        )

    def __pipeline__(self):

        dataset = tf.data.Dataset.from_tensor_slices((self._feed_dict.get('features'), self._feed_dict.get('labels'))) \
                    .shuffle(buffer_size = self._feed_dict.get('shuffle')) \
                    .batch(self._feed_dict.get('batch_size'))

        return dataset
