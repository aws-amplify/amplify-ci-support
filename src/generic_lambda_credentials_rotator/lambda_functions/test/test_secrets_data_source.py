import unittest
from unittest.mock import patch

from src.source_data_generator import secrets_data_source


class TestSecretsDataSource(unittest.TestCase):
    def test_null_environment_value(self):
        with self.assertRaises(RuntimeError):
            secrets_data_source.retrieve_secrets(configuration=None)

    @patch("src.source_data_generator.secrets_data_source.retrieve_secret")
    def test_valid_result(self, mock_retrieve_secret):
        mock_retrieve_secret.return_value = "SEKRET!"
        configuration = {"secret_key_env_variable": "secret_key"}
        result = secrets_data_source.retrieve_secrets(configuration)
        self.assertIsNotNone(result)

    @patch("src.source_data_generator.secrets_data_source.retrieve_secret")
    def test_valid_result_string(self, mock_retrieve_secret):
        mock_retrieve_secret.return_value = "SEKRET!"
        configuration = {"secret_key_env_variable": "secret_key"}
        result = secrets_data_source.retrieve_secrets(configuration)
        self.assertTrue(isinstance(result, dict))
        secret_value = result["result"]
        self.assertEqual(secret_value, "SEKRET!")

    @patch("src.source_data_generator.secrets_data_source.retrieve_secret")
    def test_valid_result_json(self, mock_retrieve_secret):
        mock_retrieve_secret.return_value = """{"GITHUB_SPM_RELEASE_USER": "user",
        "GITHUB_SPM_RELEASE_TOKEN": "token"}
        """
        configuration = {"secret_key_env_variable": "secret_key"}
        result = secrets_data_source.retrieve_secrets(configuration)
        self.assertTrue(isinstance(result, dict))

        secret_value = result["GITHUB_SPM_RELEASE_USER"]
        secret_token = result["GITHUB_SPM_RELEASE_TOKEN"]
        self.assertEqual(secret_value, "user")
        self.assertEqual(secret_token, "token")


if __name__ == "__main__":
    unittest.main()
