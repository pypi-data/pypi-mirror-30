import abc

from dataqualityhdfs.metrics.metric  import Metric


class MetricExpression(Metric, object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, metric):
        self._metric = metric

    def evaluate(self, value, metric_context):
        pass

    def get_metric_result(self):
        pass
