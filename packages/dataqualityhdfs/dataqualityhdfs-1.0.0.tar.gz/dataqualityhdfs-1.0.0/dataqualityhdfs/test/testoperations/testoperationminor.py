from dataqualityhdfs.test.testoperations.testoperation import TestOperation

class TestOperationMinor(TestOperation):

    def assert_operation(self, left_side, rigth_side):
        return left_side < rigth_side