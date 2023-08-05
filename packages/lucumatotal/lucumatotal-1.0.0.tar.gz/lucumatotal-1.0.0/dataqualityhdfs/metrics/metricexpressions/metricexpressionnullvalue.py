from dataqualityhdfs.metrics.metricresult.metricresultvalidation import MetricResultValidation
from dataqualityhdfs.metrics.metricexpressions.metricexpression import MetricExpression

class MetricExpressionNullValue(MetricExpression):

    def __init__(self, metric):
        super(MetricExpressionNullValue,self).__init__(metric)
        self._count = 0
        self._ok = 0
        self._nok = 0
        self._result_ok = []

    def evaluate(self, value, metric_context):

        self._count += 1

        if value is None:
            self._ok += 1
            self._result_ok.append()
        else:
            self._nok += 1

        self._metric.evaluate(value, metric_context)

    def get_metric_result(self):
        return MetricResultValidation(self._ok,self._nok,self._result_ok,self._count)