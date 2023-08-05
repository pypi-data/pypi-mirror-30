from TestRepresentation import TestRepresentation
from Metrics.MetricResult import MetricResultValidation
from Metrics.MetricResult import MetricResultAgg

class TestRepresentationValue(TestRepresentation):

    def get_value(self, metric_result):

        if type(metric_result) is MetricResultValidation:
            return metric_result.ok
        elif type(metric_result) is MetricResultAgg:
            return metric_result.count
        else:
            raise Exception('Invalid Type')