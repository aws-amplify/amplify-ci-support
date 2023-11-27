import os
import unittest
from unittest.mock import patch

from src.source_data_generator import lambda_env_var_data_source


class TestSecretsDataSource(unittest.TestCase):
    def test_null_environment_value(self):
        with self.assertRaises(RuntimeError):
            lambda_env_var_data_source.retrieve_lambda_env_var_value(configuration=None)

    @patch.dict(os.environ, {"variable": "SEKRET"})
    def test_valid_result(self):
        configuration = {"lambda_env_var_key": "variable"}
        result = lambda_env_var_data_source.retrieve_lambda_env_var_value(configuration)
        self.assertIsNotNone(result)

    @patch.dict(os.environ, {"variable": "SEKRET!"})
    def test_valid_result_string(self):
        configuration = {"lambda_env_var_key": "variable"}
        result = lambda_env_var_data_source.retrieve_lambda_env_var_value(configuration)
        self.assertTrue(isinstance(result, dict))
        secret_value = result["result"]
        self.assertEqual(secret_value, "SEKRET!")


if __name__ == "__main__":
    unittest.main()
