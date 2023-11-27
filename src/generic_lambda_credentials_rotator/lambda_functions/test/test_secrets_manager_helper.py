import os
import unittest
from unittest.mock import patch

import botocore.session
from botocore.stub import Stubber
from src.utils import secrets_manager_helper

session = botocore.session.get_session()
secretsmanager = session.create_client("secretsmanager", region_name=secrets_manager_helper.REGION)


class TestSecretsManagerHelper(unittest.TestCase):
    def test_null_environment_value(self):
        with self.assertRaises(ValueError):
            secrets_manager_helper.retrieve_secret("variable")

    @patch.dict(os.environ, {"variable": "some_secret_id"})
    def test_retrieve_secret(self):
        mock_secret = "SEKRET!"
        secretsmanager_stubber = Stubber(secretsmanager)
        request = {"SecretId": "some_secret_id"}
        response = {"SecretString": mock_secret}
        secretsmanager_stubber.add_response("get_secret_value", response, request)
        secretsmanager_stubber.activate()

        secret_value = secrets_manager_helper.retrieve_secret("variable", secretsmanager)

        secretsmanager_stubber.assert_no_pending_responses()

        self.assertEqual(mock_secret, secret_value)


if __name__ == "__main__":
    unittest.main()
