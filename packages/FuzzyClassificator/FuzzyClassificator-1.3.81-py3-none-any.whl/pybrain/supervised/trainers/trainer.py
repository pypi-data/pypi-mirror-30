# -*- coding: utf-8 -*-

from pybrain.utilities import Named, abstractMethod

__author__ = 'Tom Schaul, tom@idsia.ch'


class Trainer(Named):
    """ A trainer determines how to change the adaptive parameters of a module.
    It requires access to a DataSet object (which provides input-target tuples). """
    # e.g. bptt, rtrl, svm

    ds = None
    module = None

    def __init__(self, module):
        self.module = module

    def setData(self, dataset):
        """Associate the given dataset with the trainer."""
        self.ds = dataset
        if dataset:
            if dataset.indim != self.module.indim:
                raise Exception("{} not equals to {}".format(str(dataset.indim), str(self.module.indim)))

            if dataset.outdim != self.module.outdim:
                raise Exception("{} not equals to {}".format(str(dataset.outdim), str(self.module.outdim)))

    def trainOnDataset(self, dataset, *args, **kwargs):
        """Set the dataset and train.

        Additional arguments are passed on to the train method."""
        self.setData(dataset)
        self.trainEpochs(*args, **kwargs)

    def trainEpochs(self, epochs=1, *args, **kwargs):
        """Train on the current dataset for the given number of `epochs`.

        Additional arguments are passed on to the train method."""
        for dummy in range(epochs):
            self.train(*args, **kwargs)

    def train(self, *args, **kwargs):
        """Train on the current dataset, for a single epoch."""
        abstractMethod()
