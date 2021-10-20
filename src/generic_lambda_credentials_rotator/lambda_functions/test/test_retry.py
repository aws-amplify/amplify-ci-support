import unittest

from src.utils.retry import retry


class TestRetry(unittest.TestCase):
    def test_retry_retries(self):
        self.retries = 0

        @retry(max_wait=0.001, log=False)
        def exercise():
            if self.retries == 1:
                return "all good!"
            else:
                self.retries += 1
                raise RuntimeError("not good! not good at all!")

        self.assertEqual(exercise(), "all good!")

    def test_retry_raises_exception_if_retried_max_attempts(self):
        self.retries = 0

        @retry(max_attempts=3, max_wait=0.001, log=False)
        def exercise():
            self.retries += 1
            raise RuntimeError

        with self.assertRaises(RuntimeError):
            exercise()

        self.assertEqual(self.retries, 3)


if __name__ == "__main__":
    unittest.main()
