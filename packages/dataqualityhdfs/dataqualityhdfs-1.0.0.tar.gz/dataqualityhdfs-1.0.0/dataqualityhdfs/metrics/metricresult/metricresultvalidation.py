from dataqualityhdfs.metrics.metricresult.metricresult import MetricResult

class MetricResultValidation(MetricResult):

    def __init__(self,ok,nook,result_ok,count):
        super(MetricResultValidation, self).__init__(count)
        self._ok = ok
        self._result_ok = result_ok
        self._nook = nook


    @property
    def ok(self):
        return self._ok

    @property
    def nook(self):
        return self._nook

    @property
    def result_ok(self):
        return self._result_ok