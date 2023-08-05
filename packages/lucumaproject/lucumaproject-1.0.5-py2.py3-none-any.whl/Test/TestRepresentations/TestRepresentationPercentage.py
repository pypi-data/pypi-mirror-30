from TestRepresentation import TestRepresentation
from Metrics.MetricResult import MetricResultValidation
from Metrics.MetricResult import MetricResultAgg

class TestRepresentationPercentage(TestRepresentation):

    def get_value(self, metric_result):

        if type(metric_result) is MetricResultValidation:
            return (metric_result.ok/metric_result.count)*100
        elif type(metric_result) is MetricResultAgg:
            return 100
        else:
            raise Exception('Invalid Type')

