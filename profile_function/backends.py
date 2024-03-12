import logging
import timeit
from abc import ABCMeta, abstractmethod

from prometheus_client import Summary


class CollectorBackend(object):
    """
    Abstract interface to handle time collection from function or blocks
    """

    __metaclass__ = ABCMeta
    name_separator = None

    @abstractmethod
    def timer(self, name):
        """
        abstract function to implement any collection method for timing and
        collection
        :param name: name of the stats to be collected
        :return: context to collect elapsed time and send it to desired backend
        """
        pass


class StatsdBackend(CollectorBackend):
    """
    Backend to collect data to statsd
    """

    name_separator = "."

    def __init__(self, statsd):
        """
        :param statsd: StatsdClient object
        """
        self.statsd = statsd

    def timer(self, name):
        return self.statsd.timer(name)


class TimerContext(object):
    """
    A Context manager tool to handle time collection for logging backend
    """

    log_format = "{}: elapsed {}"

    def __init__(self, logger, name, log_level):
        """
        :param logger: logger object
        :param name: name of the function or block of code
        :param log_level: level of logging as python log levels
        """
        self.start = None
        self.name = name
        self.logger = logger
        self.log_level = log_level

    def __enter__(self):
        self.start = timeit.default_timer()

    def __exit__(self, *args):
        self.elapsed = timeit.default_timer() - self.start
        self.logger.log(self.log_level, self.log_format.format(self.name, self.elapsed))


class LoggerBackend(CollectorBackend):
    """
    Backend to collect data to logs
    """

    name_separator = "."

    def __init__(self, logger, log_level=logging.INFO):
        """
        :param logger: logger object to collect logs in the desired namespace
        :param log_level: level of logging as python log levels
        """
        self.logger = logger
        self.log_level = log_level

    def timer(self, name):
        return TimerContext(self.logger, name, self.log_level)


class PrometheusBackend(CollectorBackend):
    """
    Backend to collect data to prometheus
    """

    name_separator = "_"

    def __init__(self) -> None:
        self.__metrics = {}
        super().__init__()

    def timer(self, name):
        if name not in self.__metrics:
            self.__metrics[name] = Summary(name, f"Elapsed time for {name}")

        return self.__metrics[name].time()


__all__ = (
    CollectorBackend.__name__,
    LoggerBackend.__name__,
    StatsdBackend.__name__,
    PrometheusBackend.__name__,
)
