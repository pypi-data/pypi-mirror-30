# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from multiprocessing import cpu_count
from data_proxy import DataProxy


class DataPartitioner(object):
    """
    DataPartitioner is used to partition the data for each spawned process to work upon.
    number of partition are specified by the processor parameter.
    """
    __metaclass__ = ABCMeta

    def __init__(self, processors=2, data_proxy=None):
        """

        :param processors: Number of Processors. Also, the number of jobs that will be spawned.
                           Can not be more than the number of cpu's on system. Defaults to 2.
        :param data_proxy: Data to partition or instance of @data_proxy.DataProxy
                            or Nothing depending on how the partitioner is implemented.
        """
        assert cpu_count() >= processors, "processors can not be more than the number of cpu's on the system."
        self.processors = processors
        self.data_proxy = data_proxy

    @abstractmethod
    def get_partition(self):
        """
        Returns the partition for a child job.
        :return: data partition or a way for the process to get the partition.
        """
        raise NotImplemented("partitioner must implement a partition function")


class SimpleIndexPartitioner(DataPartitioner):
    """
    Example DataPartitioner where data is partitioned on indexes
    """
    def __init__(self, processors=2, data_proxy=None, start_index=0):
        """

        :param start_index: Index from where the partitions should start. Defaults to zero.
        """
        assert isinstance(data_proxy, DataProxy), "data_proxy must be as instance of @data_proxy.DataProxy"
        super(SimpleIndexPartitioner, self).__init__(data_proxy=data_proxy, processors=processors)
        self.start_index = start_index
        self.end_index = start_index
        self.data_size = self.data_proxy.get_data_size()
        self.batch_size = self.data_size / self.processors
        self.partitions = 0

    def update_indexes(self):
        """
        Update the indexes for partitioning data.
        :return: Start of the partition. Integer
        """
        pt_start = self.start_index
        if self.partitions < self.processors - 1:
            self.end_index = self.start_index + self.batch_size
        else:
            self.end_index = self.data_size
        self.partitions += 1
        self.start_index = self.end_index
        return pt_start

    def get_partition(self):
        if self.partitions < self.processors:
            pt_start = self.update_indexes()
            return 'partition_starting_at_index: {0}'.format(pt_start), pt_start, self.end_index
        return -1, -1, -1


class SimpleListPartitioner(SimpleIndexPartitioner):
    """
    Example DataPartitioner used to partition list data and return list.
    """
    def __init__(self, processors=2, data_proxy=None, start_index=0):
        super(SimpleListPartitioner, self).__init__(processors=processors, data_proxy=data_proxy,
                                                    start_index=start_index)

    def get_partition(self):
        pt_start = self.update_indexes()
        return 'partition starting at index: {0}'.format(pt_start), self.data_proxy.data[pt_start:self.end_index]
