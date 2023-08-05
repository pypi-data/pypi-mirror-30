from Granularity import Granularity

class GranularityTemporal(Granularity):

    def __init__(self, year, month,week,day,hour,minute,second,granularity_time_interval):
        self._year = year
        self._month = month
        self._week = week
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second
        self._granularity_time_interval = granularity_time_interval


    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def week(self):
        return self._week

    @property
    def day(self):
        return self._day

    @property
    def hour(self):
        return self._hour

    @property
    def minute(self):
        return self._minute

    @property
    def granularity_time_interval(self):
        return self._granularity_time_interval


    def get_granularity(self):
         return "hola"
