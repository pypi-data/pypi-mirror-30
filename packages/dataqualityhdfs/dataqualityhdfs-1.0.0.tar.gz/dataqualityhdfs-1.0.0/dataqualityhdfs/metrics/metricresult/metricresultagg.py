from dataqualityhdfs.metrics.metricresult.metricresult import MetricResult

class MetricResultAgg(MetricResult):

    def __init__(self,count):
        super(MetricResult, self).__init__(count)