# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class JobResult(object):
    """
    JobResult represents the object returned by the spawned processes.
    """
    def __init__(self, job_id, result=None):
        """

        :param job_id: The job id of process returning the JobResult object.
        :param result: The result from the process.
        """
        self.job_id = job_id
        self.result = result


class JobSuccess(JobResult):
    """
    JobSuccess represents the successful execution of spawned process.
    """
    def __init__(self, job_id, result=None):
        """

        :param job_id: The job id of process returning the JobResult object.
        :param result: The result from the process.
        """
        super(JobSuccess, self).__init__(job_id, result)


class JobError(JobResult):
    """
    JobError represents the failed execution of spawned process.
    """
    def __init__(self, job_id, result=None):
        """

        :param job_id: The job id of process returning the JobResult object.
        :param result: The result from the process.
        """
        super(JobError, self).__init__(job_id, result)


class ResultManager(object):
    """
    utility class for post processing the results from the spawned processes.
    """
    __metaclass__ = ABCMeta

    def __init__(self, results, errors):
        """

        :param results: The results from the process.
        :param errors: The errors from the process.
        """
        self.results = results
        self.errors = errors

    def add_results(self, result):
        """
        Add the result from individual processes to self.results or self.errors based on the result type.
        :param result: The result from the process. Instance of JobResult.
        :return: None
        """
        if type(result).__name__ == JobSuccess.__name__:
            self.add_success(result)
        elif type(result).__name__ == JobError.__name__:
            self.add_error(result)
        else:
            raise TypeError("job result must be an instance of {0} or {1}".format(JobSuccess.__name__,
                                                                                  JobError.__name__))

    @abstractmethod
    def add_success(self, result):
        """
        Add the result from individual processes to self.results.
        :param result: instance of JobSuccess.
        :return: None
        """
        raise NotImplementedError("ResultManager must implement add_success")

    @abstractmethod
    def add_error(self, error):
        """
        Add the result from individual processes to self.errors.
        :param error: instance of JobError.
        :return: None
        """
        raise NotImplementedError("ResultManager must implement add_errors")

    def show_results(self):
        """
        return the combined result of all spawned processes.
        :return: self.results
        """
        return self.results

    def show_errors(self):
        """
        return the combined error of all spawned processes.
        :return: self.errors
        """
        return self.errors


class ListResultManager(ResultManager):
    """
    Example ResultManager where results and errors are stored as lists.
    """
    def __init__(self):
        super(ListResultManager, self).__init__([], [])

    def add_success(self, result):
        assert type(result).__name__ == JobSuccess.__name__,\
            "job result must be an instance of {0}".format(JobSuccess.__name__)
        self.results.append(result)

    def add_error(self, error):
        assert type(error).__name__ == JobError.__name__, \
            "job error must be an instance of {0}".format(JobError.__name__)
        self.errors.append(error)
