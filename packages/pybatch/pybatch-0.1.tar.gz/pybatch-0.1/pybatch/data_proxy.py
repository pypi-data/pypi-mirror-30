# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class DataProxy(object):
    """
    DataProxy is a wrapper for the the data on part of which the function to parallelize will operate upon.
    """
    __metaclass__ = ABCMeta

    def __init__(self, data=None):
        """

        :param data: data
        """
        self.data = data

    @abstractmethod
    def get_data_size(self):
        """
        Returns the size of the data.
        Primarily used by @partitioner.DataPartitioner to get the size of the data to partition.
        :return: Size of self.data
        """
        raise NotImplemented("Data proxy must implement get_data_size function")


class ListDataProxy(DataProxy):
    """
    Example DataProxy where the encapsulated data is a list of objects.
    """
    def __init__(self, data=None):
        super(ListDataProxy, self).__init__(data)

    def get_data_size(self):
        return len(self.data)
