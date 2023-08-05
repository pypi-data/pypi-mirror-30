from dataqualityhdfs.metrics.metricresult.metricresultvalidation import MetricResultValidation
from dataqualityhdfs.metrics.metricresult.metricresultagg import MetricResultAgg

from dataqualityhdfs.test.testrepresentations.testrepresentation import TestRepresentation


class TestRepresentationValue(TestRepresentation):

    def get_value(self, metric_result):

        if type(metric_result) is MetricResultValidation:
            return metric_result.ok
        elif type(metric_result) is MetricResultAgg:
            return metric_result.count
        else:
            raise Exception('Invalid Type')