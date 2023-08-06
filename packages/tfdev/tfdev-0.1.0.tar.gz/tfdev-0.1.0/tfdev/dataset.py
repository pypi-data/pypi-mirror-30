#!/usr/bin/env python3
import tensorflow as tf

from abc import ABC, abstractmethod
from .collections import FeedDict

class Dataset(ABC):

    def __init__(self, files, batch_size, max_batch_size, shuffle, validation = None, parallel_call = 1):

        self.__feed_dict = FeedDict()

        self.__feed_dict.add(
            tensor = tf.placeholder(tf.string, shape = [None]),
            name = 'files',
            train = files,
            valid = validation,
        )

        self.__feed_dict.add(
            tensor = tf.placeholder(tf.int64),
            name = 'shuffle',
            train = shuffle,
            valid = 1,
        )

        self.__feed_dict.add(
            tensor = tf.placeholder(tf.int64),
            name = 'batch_size',
            train = batch_size,
            valid = max_batch_size,
        )

        self.__iterator = self.__pipline__(parallel_call = parallel_call).make_initializable_iterator()

    @property
    def initializer(self):
        return self.__iterator.initializer

    @property
    def iterator(self):
        return self.__iterator.get_next()

    @abstractmethod
    def __parse_tfrecord__(self, example_proto):
        return example_proto

    def __pipline__(self, parallel_call):

        dataset = tf.data.TFRecordDataset(self.__feed_dict.get('files')) \
                    .map(self.__parse_tfrecord__, num_parallel_calls = parallel_call) \
                    .shuffle(buffer_size = self.__feed_dict.get('shuffle')) \
                    .batch(self.__feed_dict.get('batch_size'))

        return dataset

    def get_feed_dict(self, train = False):
        return self.__feed_dict.get_feed_dict(train = train)
