import logging
from enum import Enum

METRIC_PROFILE_NAMESPACE = "functions_profile"

SEPARATOR = "."


class MetricMode(Enum):
    TIME = "time"


class ProfileFunction(object):
    def __init__(self, backend, namespace=METRIC_PROFILE_NAMESPACE):
        self.backend = backend
        self.namespace = namespace

    @staticmethod
    def get_name(name, group, block=None, separator=SEPARATOR):
        """
        extract a function path

        args:
            func: a function to extract its path and function name separated with dot character given as a parameter
            group: metric grouping scope
            block: specific block of the function (could be None)
        returns:
            function path separated with dot character param
        """

        path = f"{group}{separator}{name}"
        if block:
            path += f"{separator}{block}"
        return path

    def get_profiling_metric_name(self, name, group, block=None, sep=None):
        """
        returns metric name to save in graphite

        Args:
            name: function to find metric name for profiling
            group: scope to group the function in stats
            block: specific block of the function (could be None)
            sep: separator for metric name

        Returns:
            metric name to save it is metric backend
        """
        _separator = sep or self.backend.name_separator
        path = self.get_name(name, group, block=block, separator=_separator)
        return f"{self.namespace}{_separator}{MetricMode.TIME.value}{_separator}{path}"

    def profile_block(self, block_name, group="other", block=None):
        """
        Records timing information for a function or a block inside a function.

        Args:
            block_name: function to find metric name for profiling or the name in string
            group: scope to group the function in stats
            block: specific block of the function (could be None)

        Returns:
            timer object
        """
        try:
            metric_name = self.get_profiling_metric_name(block_name, group, block=block)
            return self.backend.timer(metric_name)
        except Exception as e:
            logging.error(f"Error profiling block {block_name}: {e}")

    def profile_function(self, name=None, group="other"):
        """
        decorator to profile function, send how many and how much time a
        function call takes
        Args:
            name: force function path
            group: group name of a function to profile otherwise the group
            name will be 'other'

        Returns:
            profile enabled function to use
        """

        def internal(func):
            def wrapper(*args, **kwargs):
                function_name = func if name is not None else func.__name__
                try:
                    with self.profile_block(function_name, group):
                        return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Error profiling function {function_name}: {e}")
            return wrapper
        return internal


__all__ = (ProfileFunction.__name__,)
