#!/usr/bin/env python3
import os
import tensorflow as tf

from math import inf
from abc import ABC

class Callback(ABC):

    def on_compile_end(self, metric_op):
        pass

    def on_epoch_end(self, epoch, metric_op, model):
        return True

    def on_epoch_start(self, epoch, metric_op, model):
        return True

    def on_step_end(self, model):
        return True

    def on_step_start(self, model):
        return True

class EarlyStopping(Callback):

    def __init__(self, epochs, minimum = True):

        self.epochs = epochs
        self.minimum = minimum

        self.__i = 0
        self.__mon_val = inf if minimum else -inf

    def on_epoch_end(self, epoch, metric_op, model):

        metric = metric_op.eval()

        if (self.minimum and metric < self.__mon_val) or (not self.minimum and metric > self.__mon_val):
            self.__mon_val = metric
            self.__i = epoch

        if epoch - self.__i > self.epochs:
            return False

        return True

class TensorBoard(Callback):

    def __init__(self, logdir, name = 'metrics'):
        self.logdir = logdir
        self.name = name

    def on_compile_end(self, metric_op):
        tf.summary.scalar(self.name, metric_op)
        self.__tensorboard_op = tf.summary.merge_all()
        self.__writer = tf.summary.FileWriter(self.logdir, tf.get_default_session().graph)

    def on_epoch_end(self, epoch, metric_op, model):
        tb, metric = tf.get_default_session().run([self.__tensorboard_op, metric_op])
        self.__writer.add_summary(tb, epoch)

        return True

class CheckPoint(Callback):

    def __init__(self, path, best_only = False, minimum = True):
        if not os.path.isdir(path):
            os.makedirs(path)

        self.path = path + '/model.ckpt'
        self.best_only = best_only
        self.minimum = minimum

        self.__mon_val = inf if minimum else -inf

    def on_epoch_end(self, epoch, metric_op, model):

        if self.best_only:
            metric = metric_op.eval()

            if (self.minimum and self.__mon_val > metric) or (not self.minimum and self.__mon_val < metric):
                model.save(path = self.path)
                print("From %f to %f, save best model to %s" % (self.__mon_val, metric, self.path))
                self.__mon_val = metric

        else:
            model.save(path = self.path, step = epoch)
            print("Save model to %s-%d" % (self.path, epoch))

        return True
