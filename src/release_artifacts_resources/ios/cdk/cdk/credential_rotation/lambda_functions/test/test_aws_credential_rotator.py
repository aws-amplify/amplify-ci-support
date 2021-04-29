import os
import unittest
from datetime import datetime
from unittest.mock import patch

import botocore.session
from botocore.stub import ANY, Stubber
from src.source_data_generator import aws_session_credential_source as rotator
from src.source_data_generator.aws_session_credential_source import generate_session_credentials

# IAM materials for stubs. These are not real credentials, rather they are
# conventional examples used in AWS documentation. See https://bit.ly/2XsAkBq.
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
expiration = datetime(2015, 1, 1)


session = botocore.session.get_session()
iam = session.create_client("iam", region_name=rotator.REGION)
sts = session.create_client("sts", region_name=rotator.REGION)


class TestAWSCredentialRotator(unittest.TestCase):
    @patch.dict(
        os.environ, {"IAM_USERNAME": "username", "IAM_ROLE": "arn:::CIRCLECI_EXECUTION_ROLE"}
    )
    def test_handler_rotates_credentials(self):
        # Initializer stubbers
        iam_stubber = Stubber(iam)
        sts_stubber = Stubber(sts)
        stubbers = [iam_stubber, sts_stubber]

        # IAM stub
        create_request = {"UserName": "username"}
        create_response = {
            "AccessKey": {
                "UserName": "username",
                "AccessKeyId": access_key_id,
                "Status": "Active",
                "SecretAccessKey": secret_access_key,
            }
        }
        delete_request = {"UserName": "username", "AccessKeyId": access_key_id}
        iam_stubber.add_response("create_access_key", create_response, create_request)
        iam_stubber.add_response("delete_access_key", {}, delete_request)

        # STS stub
        sts_request = {
            "RoleArn": ANY,
            "RoleSessionName": ANY,
            "DurationSeconds": rotator.SESSION_DURATION_SECONDS,
        }
        sts_response = {
            "Credentials": {
                "AccessKeyId": access_key_id,
                "SecretAccessKey": secret_access_key,
                "SessionToken": session_token,
                "Expiration": expiration,
            }
        }
        sts_stubber.add_response("assume_role", sts_response, sts_request)

        for stubber in stubbers:
            stubber.activate()

        result = generate_session_credentials(
            configuration=self.mock_configuration(), iam=iam, sts=sts
        )

        for stubber in stubbers:
            stubber.assert_no_pending_responses()

        self.assertIn("AccessKeyId", result)
        self.assertIn("SecretAccessKey", result)
        self.assertIn("SessionToken", result)

    def test_generate_credential_with_null_configuration(self):
        with self.assertRaises(RuntimeError):
            generate_session_credentials(configuration=None)

    def mock_configuration(self):
        return {"user_env_variable": "IAM_USERNAME", "iam_role_env_variable": "IAM_ROLE"}

    def mock_destination_mapping(self):
        return [
            {"destination_key_name": "XCF_ACCESS_KEY_ID", "result_value_key": "AccessKeyId"},
            {
                "destination_key_name": "XCF_SECRET_ACCESS_KEY",
                "result_value_key": "SecretAccessKey",
            },
            {"destination_key_name": "XCF_SESSION_TOKEN", "result_value_key": "SessionToken"},
        ]


if __name__ == "__main__":
    unittest.main()
