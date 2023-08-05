class Interface:

    def __init__(self,granularities,tables):
        self._granularities = granularities
        self._tables = tables

    @property
    def granularities(self):
        return self._granularities

    @property
    def tables(self):
        return self._tables

