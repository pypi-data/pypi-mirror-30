from dataqualityhdfs.test.testresult import TestResult

class Test:

    def __init__(self,threshold,test_representation,test_operation,metric):
        self._threshold = threshold
        self._test_representation = test_representation
        self._test_operation = test_operation
        self._metric = metric
        self._test_result = TestResult.FAIL

    @property
    def test_representation(self):
        return self._test_representation

    @property
    def test_operation(self):
        return self._test_operation

    @property
    def threshold(self):
        return self._threshold

    @property
    def metric(self):
        return self._metric

    @property
    def test_result(self):
        return self._test_result

    def assert_test(self):
        metric_result = self._metric.get_metric_result()
        if(self._test_operation.assert_operation(self._test_representation.get_value(metric_result),self._threshold)):
            self._test_result = TestResult.PASS
        else:
            self._test_result = TestResult.FAIL