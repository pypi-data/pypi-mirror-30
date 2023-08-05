import abc

class Granularity(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_granularity(self):
        pass