# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue, Pipe, Lock
from partitioner import DataPartitioner
from result import ResultManager, ListResultManager, JobError, JobSuccess

DEFAULT_PARTITION_KEY = 'data_partition'
SHARED_LOCK_KEY = 'shared_lock'


class JobExecutor(object):
    """
    Base class for job executor that will run the worker function on different processors in parallel.
    """
    __metaclass__ = ABCMeta

    def __init__(self, worker=None, data_partitioner=None, result_manager=None):
        """

        :param worker: The worker function to run in parallel. Must be a callable.
        :param data_partitioner: Instance of DataPartitioner to partition the source data.
        :param result_manager: Instance of @result.ResultManager to return the results of all the jobs.
        """
        assert isinstance(data_partitioner, DataPartitioner),\
            "data_partitioner must be an instance of {0}".format(DataPartitioner.__name__)
        if result_manager is not None:
            assert isinstance(result_manager, ResultManager), \
                "result_manager must be an instance of {0}".format(ResultManager.__name__)
            self.result_manager = result_manager
        else:
            self.result_manager = ListResultManager()

        self.data_partitioner = data_partitioner
        self.processors = self.data_partitioner.processors
        self.worker = worker
        self.processes = []

    @abstractmethod
    def response_holder(self):
        """
        Object to hold the output of each spawned process.
        Example a Queue or Pipe.
        :return: An artifact that can hold the response from each process.
        """
        raise NotImplementedError("JobExecutor must implement a response holder function.")

    @abstractmethod
    def format_response(self):
        """
        Function to format the response from each spawned process.
        :return: ResultManager
        """
        return self.result_manager

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Function to execute the worker function in parallel.
        :param args: any/all arguments for the original worker function + the response holder.
        :param kwargs: any/all keyworded arguments for the original worker function.
        :return: ResultManager
        """
        raise NotImplementedError()

    def safe_worker(self, *args, **kwargs):
        """
        Wraps the original worker function in try except to distinguish successful and failed execution.
        :param args: any/all arguments for the original worker function + the response holder.
        :param kwargs: any/all keyworded arguments for the original worker function
                        + the job_id with key=job_id.
                        + the data partition with key=@executer.DEFAULT_PARTITION_KEY
                        + the @multiprocessing.Lock object with key=@executer.SHARED_LOCK_KEY.
                        kwargs['SHARED_LOCK_KEY'] can be used by the worker process to safely access the shared resources
                        using acquire and release functions
        :return: JobResult
        """
        try:
            result = self.worker(*args[2:], **kwargs)
            worker_result = JobSuccess(kwargs['job_id'], result)
        except Exception as e:
            worker_result = JobError(kwargs['job_id'], e)
        return worker_result

    def create_and_start_process(self, *args, **kwargs):
        """
        Function to create the required data, additional arguments and start the process.
        Adds the partition data, job_id and lock object to the arguments for safe_worker function.
        :param args: any/all arguments for the original worker function.
        :param kwargs: any/all keyworded arguments for the original worker function
                        + the job_id with key=job_id.
        :return: self.response_holder()
        """
        assert callable(self.worker), ""
        lock = Lock()
        partition_id, partition_data = self.data_partitioner.get_partition()
        kwargs[SHARED_LOCK_KEY] = lock
        kwargs[DEFAULT_PARTITION_KEY] = partition_data
        kwargs['job_id'] = kwargs.get('job_id', 'partition_id: ') + partition_id
        response = self.response_holder()
        p = Process(target=self.safe_worker, args=response + args, kwargs=kwargs)
        self.processes.append(p)
        p.start()
        return response

    def wait(self):
        """
        Wrapper function to wait until all the spawned jobs finish.
        :return:
        """
        for p in self.processes:
            p.join()


class QueuedJobExecutor(JobExecutor):
    """
    JobExecutor where the output of spawned processes is added to a @multiprocessing.Queue
    Use this if the expected total response size is small.
    Process hangs if the response size is more than the queue max size.
    """
    def __init__(self, worker=None, data_partitioner=None, result_manager=None):
        super(QueuedJobExecutor, self).__init__(worker=worker, data_partitioner=data_partitioner,
                                                result_manager=result_manager)
        self.response = (Queue(),)

    def safe_worker(self, *args, **kwargs):
        result = super(QueuedJobExecutor, self).safe_worker(*args, **kwargs)
        args[0].put(result)

    def response_holder(self):
        return self.response

    def format_response(self):
        self.wait()
        response = self.response[0]
        while not response.empty():
            self.result_manager.add_results(response.get())
        return self.result_manager

    def execute(self, *args, **kwargs):
        for i in range(self.processors):
            kwargs['job_id'] = 'Job_{0}: partition_id: '.format(i)
            self.create_and_start_process(*args, **kwargs)
        return self.format_response()


class PipedJobExecutor(JobExecutor):
    """
    JobExecutor where the output of spawned processes is communicated to parent process using a @multiprocessing.Pipe
    Use this if the expected total response size is high.
    Each spawned process communicates with the parent with its own duplex pipe.
    """
    def __init__(self, worker=None, data_partitioner=None, result_manager=None):
        super(PipedJobExecutor, self).__init__(worker=worker, data_partitioner=data_partitioner,
                                               result_manager=result_manager)

    def safe_worker(self, *args, **kwargs):
        result = super(PipedJobExecutor, self).safe_worker(*args, **kwargs)
        args[1].send(result)
        args[1].close()

    def response_holder(self):
        return Pipe()

    def format_response(self, *args, **kwargs):
        for p in kwargs['pipes']:
            self.result_manager.add_results(p.recv())
        self.wait()
        return self.result_manager

    def execute(self, *args, **kwargs):
        pipes = []
        for i in range(self.processors):
            kwargs['job_id'] = 'Job_{0}: partition_id: '.format(i)
            parent_conn, child_conn = self.create_and_start_process(*args, **kwargs)
            pipes.append(parent_conn)
        return self.format_response(pipes=pipes)


class ExecutorCommType(object):
    """
    Class that holds the types of JobExecutors.
    """
    queue = 'queue'
    pipe = 'pipe'


class Parallelize(object):
    """
    Decorator for parallel execution of a function.
    """
    def __init__(self, executor_factory=None, executor_type=ExecutorCommType.queue, data_partitioner=None,
                 result_manager=None):
        """

        :param executor_factory: A function that returns the instance of JobExecutor.
        :param executor_type: ExecutorCommType. Used only if executor_factory is None.
        :param data_partitioner: Instance of @partitioner.DataPartitioner.
        :param result_manager: Instance of @result.ResultManager.
        """
        if executor_factory is not None:
            self.executor = executor_factory()
            assert isinstance(self.executor, JobExecutor), "executor_factory "
        else:
            if executor_type == ExecutorCommType.queue:
                self.executor = QueuedJobExecutor(worker=None, data_partitioner=data_partitioner,
                                                  result_manager=result_manager)
            if executor_type == ExecutorCommType.pipe:
                self.executor = PipedJobExecutor(worker=None, data_partitioner=data_partitioner,
                                                 result_manager=result_manager)

    def __call__(self, f):
        self.executor.worker = f
        return self.executor.execute


# if __name__ == "__main__":
#
#     class ListDataProxy(DataProxy):
#
#         def __init__(self):
#             super(ListDataProxy, self).__init__([i for i in range(100)])
#             self.data_size = len(self.data)
#
#         def get_data_size(self):
#             return self.data_size
#
#         def get_partition(self, *args, **kwargs):
#             # partiton_indexes = kwargs[DEFAULT_PARTITION_KEY]
#             return args, kwargs  # self.data[partiton_indexes[0]:partiton_indexes[1]]
#
#     Data = ListDataProxy()
#
#
#     @Parallelize(data_partitioner=SimpleIndexPartitioner(data_proxy=Data, processors=1),
#                  result_manager=ListResultManager())
#     def test_worker(*args, **kwargs):
#         return Data.get_partition(*args, **kwargs)
#
#
#     response = test_worker(1, 2)
#     print(response.show_results()[0].__dict__)
