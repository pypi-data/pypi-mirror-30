import abc

class MetricResult(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,count):
        self._count = count

    @property
    def count(self):
        return self._count