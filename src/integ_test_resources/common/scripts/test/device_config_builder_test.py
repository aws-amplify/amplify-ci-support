#!/usr/bin/env python3

import json
import os
import pathlib
import sys
import unittest

from device_config_builder import DeviceConfigBuilder

sys.path.append(str(pathlib.Path(__file__).parent.absolute()) + "/..")


class TestDeviceConfigBuilder(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestDeviceConfigBuilder, self).__init__(*args, **kwargs)
        self.underTest = DeviceConfigBuilder("android")

    def test_build_package_data(self):
        prefix = "/mobile-sdk/android"
        parameters = self.load_parameters()

        package_data = self.underTest.build_package_data(prefix, parameters)

        self.assertEqual(
            {
                "apigateway": {
                    "api_key": "someapikeyhere",
                    "endpoint_us_east_1":
                        "https://redactedapi.execute-api.us-east-1.amazonaws.com/prod/",
                    "endpoint_us_east_2":
                        "https://redactedapi.execute-api.us-east-2.amazonaws.com/prod",
                },
                "core": {"identity_pool_id": "us-east-1:00000000-3c37-43d7-8fe6-3e0a65985b02"},
            },
            package_data,
        )

    def test_build_package_data_with_nesting(self):
        params = [
            {"Name": "/mobile-sdk/android/suite/foo/bar/baz", "Value": "foo-bar-baz-val"},
            {"Name": "/mobile-sdk/android/suite/potato/bar/baz", "Value": "potato-bar-baz-val"},
        ]
        prefix = "/mobile-sdk/android"

        package_data = self.underTest.build_package_data(prefix, params)

        self.assertEqual(
            {
                "suite": {
                    "foo": {"bar": {"baz": "foo-bar-baz-val"}},
                    "potato": {"bar": {"baz": "potato-bar-baz-val"}},
                }
            },
            package_data,
        )

    def test_get_credential_data(self):
        environment_variables = {
            "AWS_ACCESS_KEY_ID": "accessKey",
            "AWS_SECRET_ACCESS_KEY": "secretKey",
            "AWS_SESSION_TOKEN": "sessionToken",
        }
        for key, value in environment_variables.items():
            os.environ[key] = value

        credentials_data = self.underTest.get_credentials_data()

        self.assertEqual(
            {"accessKey": "accessKey", "secretKey": "secretKey", "sessionToken": "sessionToken"},
            credentials_data,
        )

    def test_aws_config_from_environment(self):
        environment_variables = {
            "AWS_ACCESS_KEY_ID": "accessKey",
            "AWS_SECRET_ACCESS_KEY": "secretKey",
            "AWS_SESSION_TOKEN": "sessionToken",
            "AWS_DEFAULT_REGION": "defaultRegion",
        }
        for key, value in environment_variables.items():
            os.environ[key] = value

        aws_config = self.underTest.aws_config_from_environment()

        self.assertEqual(
            DeviceConfigBuilder.AWSConfig(
                "accessKey", "secretKey", "sessionToken", "defaultRegion"
            ),
            aws_config,
        )

    def load_parameters(self):
        """
        This method "stubs" out the result of calling SSM's
        get-parameters-by-prefix
        """
        current_dir_abs_path = str(pathlib.Path(__file__).parent.absolute())
        parameter_json_abs_path = current_dir_abs_path + "/all-parameters.json"
        data = ""
        with open(parameter_json_abs_path, "r") as parameters_file:
            data = " ".join(parameters_file.readlines())

        return json.loads(data)["Parameters"]


if __name__ == "__main__":
    unittest.main()
