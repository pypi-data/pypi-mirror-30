import abc

class Source(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def retrieve_dataset(self):
        pass


