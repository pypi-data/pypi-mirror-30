import abc

class TestOperation(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def assert_operation(self,left_side,rigth_side):
        pass