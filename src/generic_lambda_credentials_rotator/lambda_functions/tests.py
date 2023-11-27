import unittest
from test import test_aws_credential_rotator, test_circleci, test_retry


def suite():
    suite = unittest.TestSuite()
    suite.addTests(test_retry)
    suite.addTests(test_aws_credential_rotator)
    suite.addTests(test_circleci)
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
