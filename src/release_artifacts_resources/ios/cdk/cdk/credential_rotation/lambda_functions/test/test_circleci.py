import os
import unittest
from unittest.mock import Mock, call, patch

import botocore.session
from botocore.stub import Stubber
from src.destination import circleci

session = botocore.session.get_session()
secretsmanager = session.create_client("secretsmanager", region_name=circleci.REGION)

access_key_id = "AKIAIOSFODNN7EXAMPLE"
secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY"
session_token = (
    "AQoDYXdzEPT//////////wEXAMPLEtc764bNrC9SAPBSM22wDOk"
    + "4x4HIZ8j4FZTwdQWLWsKWHGBuFqwAeMicRXmxfpSPfIeoIYRqTf"
    + "lfKD8YUuwthAx7mSEI/qkPpKPi/kMcGdQrmGdeehM4IC1NtBmUp"
    + "p2wUE8phUZampKsburEDy0KPkyQDYwT7WZ0wq5VSXDvp75YU9HF"
    + "vlRd8Tx6q6fE8YQcHNVXAkiY9q6d+xo0rKwT38xVqr7ZD0u0iPP"
    + "kUL64lIZbqBAz+scqKmlzm8FDrypNC9Yjc8fPOLn9FX9KSYvKTr"
    + "4rvx3iSIlTJabIQwj2ICCR/oLxBA=="
)


class TestCircleCIDestination(unittest.TestCase):
    def test_generate_credential_with_null_variables(self):
        with self.assertRaises(RuntimeError):
            circleci.update_environment_variables(variables=None, configuration=None)

    def test_generate_credential_with_null_configuration(self):
        with self.assertRaises(RuntimeError):
            circleci.update_environment_variables(
                variables=self.mock_variables(), configuration=None
            )

    @patch.dict(os.environ, {"CIRCLE_CI_IOS_SDK_API_TOKEN": "arn:::xxx"})
    @patch("src.destination.circleci.requests.post")
    def test_updates_variables(self, post):
        secretsmanager_stubber = Stubber(secretsmanager)
        request = {"SecretId": "arn:::xxx"}
        response = {"SecretString": "SEKRET!"}
        secretsmanager_stubber.add_response("get_secret_value", response, request)

        post.return_value = Mock()
        post.return_value.status_code = 200

        secretsmanager_stubber.activate()
        circleci.update_environment_variables(
            variables=self.mock_variables(),
            configuration=self.mock_configuration(),
            secretsmanager=secretsmanager,
        )
        secretsmanager_stubber.assert_no_pending_responses()

        url = "https://circleci.com/api/v2/project/gh/aws-amplify/aws-sdk-ios/envvar"
        header = {"Circle-Token": "SEKRET!"}
        values = {
            "XCF_ACCESS_KEY_ID": access_key_id,
            "XCF_SECRET_ACCESS_KEY": secret_access_key,
            "XCF_SESSION_TOKEN": session_token,
        }
        for i, (key, value) in enumerate(values.items()):
            expected_json = {"name": key, "value": value}
            expected = call(url, json=expected_json, headers=header)
            self.assertEqual(post.mock_calls[i], expected)

    def mock_variables(self):
        return {
            "XCF_ACCESS_KEY_ID": access_key_id,
            "XCF_SECRET_ACCESS_KEY": secret_access_key,
            "XCF_SESSION_TOKEN": session_token,
        }

    def mock_configuration(self):
        return {
            "type": "cci_env_variable",
            "description": "Circle CI environment variable for AWS SDK iOS repo",
            "github_path": "aws-amplify/aws-sdk-ios",
            "circleci_api_token_secret_arn_lambda_env_var_key": "CIRCLE_CI_IOS_SDK_API_TOKEN",
        }


if __name__ == "__main__":
    unittest.main()
