from dataqualityhdfs.metrics.metricresult.metricresultvalidation import MetricResultValidation
from dataqualityhdfs.metrics.metricresult.metricresultagg import MetricResultAgg

from dataqualityhdfs.test.testrepresentations.testrepresentation import TestRepresentation


class TestRepresentationPercentage(TestRepresentation):

    def get_value(self, metric_result):

        if type(metric_result) is MetricResultValidation:
            return (metric_result.ok/metric_result.count)*100
        elif type(metric_result) is MetricResultAgg:
            return 100
        else:
            raise Exception('Invalid Type')

