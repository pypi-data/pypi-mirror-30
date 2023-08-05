class Column:

    def __init__(self,name,map_type,metric):
        self._name = name
        self.map_type = map_type
        self._metric = metric

    @property
    def name(self):
        return self._name

    @property
    def map_type(self):
        return  self._map_type

    @property
    def metric(self):
        return self._metric