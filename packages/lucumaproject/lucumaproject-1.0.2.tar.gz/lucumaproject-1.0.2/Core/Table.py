class Table:

    def __init__(self,granularity,columns,metrics,tests,source,data_set):
        self._granularity = granularity
        self._columns = columns
        self._metrics = metrics
        self._source = source
        self._data_set = data_set
        self._tests = tests
        if(data_set is None):
            self._is_load_information = False
        else:
            self._is_load_information = True

    @property
    def granularity(self):
        return self._granularity

    @property
    def columns(self):
        return self._columns

    @property
    def metrics(self):
        return self._metrics

    @property
    def tests(self):
        return self._tests

    @property
    def data_set(self):
        return self._data_set

    @data_set.setter
    def data_set(self, value):
        if (value is None):
            self._is_load_information = False
        else:
            self._is_load_information = True
        self._data_set = value

    @property
    def source(self):
        return self._source

    @property
    def is_load_information(self):
        return self._is_load_information

    def load_dataset(self):
        if(self._source is not None):
            self._data_set = self._source.retrieve_dataset()
            self._is_load_information = True
