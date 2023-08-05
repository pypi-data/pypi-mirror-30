import abc

class TestRepresentation(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_value(self, metric_result):
        pass