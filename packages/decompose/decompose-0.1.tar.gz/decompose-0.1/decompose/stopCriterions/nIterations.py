import tensorflow as tf
from tensorflow import Tensor


class NIterations(object):
    def __init__(self, nIterations=100, ns="stopCriterion"):
        self.__nIterations = nIterations
        self.__ns = ns

    def init(self):
        with tf.variable_scope(self.__ns):
            iterationNumberVar = tf.get_variable("iterationNumber",
                                                 dtype=tf.int32,
                                                 initializer=0)
            self.iterationNumberVar = iterationNumberVar
            stopVar = tf.get_variable("stop",
                                      dtype=tf.bool,
                                      initializer=False)
            self.__stopVar = stopVar

    def update(self, model, X: Tensor):
        u0 = tf.assign(self.iterationNumberVar, self.iterationNumberVar + 1)
        u1 = tf.assign(self.stopVar, tf.greater_equal(self.iterationNumberVar,
                                                      self.__nIterations))
        return([u0, u1])

    @property
    def stopVar(self):
        return(self.__stopVar)
