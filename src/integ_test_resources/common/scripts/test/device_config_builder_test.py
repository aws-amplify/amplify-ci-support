#!/usr/bin/env python3

import json
import os
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.append(str(pathlib.Path(__file__).parent.absolute()) + "/..")
from device_config_builder import DeviceConfigBuilder


class TestDeviceConfigBuilder(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestDeviceConfigBuilder, self).__init__(*args, **kwargs)
        self.underTest = DeviceConfigBuilder("android")

    def test_build_package_data(self):
        prefix = "/mobile-sdk/android"
        parameters = TestDeviceConfigBuilder.load_parameters()

        package_data = self.underTest.build_package_data(prefix, parameters)

        self.assertEqual(
            {
                "apigateway": {
                    "api_key": "someapikeyhere",
                    "endpoint_us_east_1": "https://redactedapi.execute-api.us-east-1.amazonaws.com/prod/",  # noqa: E501
                    "endpoint_us_east_2": "https://redactedapi.execute-api.us-east-2.amazonaws.com/prod",  # noqa: E501
                },
                "core": {"identity_pool_id": "us-east-1:00000000-3c37-43d7-8fe6-3e0a65985b02"},
            },
            package_data,
        )

    def test_build_package_data_with_nesting(self):
        params = [
            {"Name": "/mobile-sdk/android/suite/foo/bar/baz", "Value": "foo_bar_baz_val"},
            {"Name": "/mobile-sdk/android/suite/potato/bar/baz", "Value": "potato_bar_baz_val"},
        ]
        prefix = "/mobile-sdk/android"

        package_data = self.underTest.build_package_data(prefix, params)

        self.assertEqual(
            {
                "suite": {
                    "foo": {"bar": {"baz": "foo_bar_baz_val"}},
                    "potato": {"bar": {"baz": "potato_bar_baz_val"}},
                }
            },
            package_data,
        )

    def test_get_credential_data(self):
        with patch.dict(
            os.environ,
            {
                "AWS_ACCESS_KEY_ID": "accessKey",
                "AWS_SECRET_ACCESS_KEY": "secretKey",
                "AWS_SESSION_TOKEN": "sessionToken",
                "AWS_DEFAULT_REGION": "defaultRegion",
            },
        ):
            credentials_data = self.underTest.get_credentials_data()
            self.assertEqual(
                {
                    "accessKey": "accessKey",
                    "secretKey": "secretKey",
                    "sessionToken": "sessionToken",
                },
                credentials_data,
            )

    def test_aws_config_from_environment(self):
        with patch.dict(
            os.environ,
            {
                "AWS_ACCESS_KEY_ID": "accessKey",
                "AWS_SECRET_ACCESS_KEY": "secretKey",
                "AWS_SESSION_TOKEN": "sessionToken",
                "AWS_DEFAULT_REGION": "defaultRegion",
            },
        ):
            aws_config = self.underTest.aws_config_from_environment()
            self.assertEqual(
                DeviceConfigBuilder.AWSConfig(
                    "accessKey", "secretKey", "sessionToken", "defaultRegion"
                ),
                aws_config,
            )

    @staticmethod
    def load_parameters():
        """
        This method "stubs" out the result of calling SSM's
        get-parameters-by-prefix
        """
        current_dir_abs_path = str(pathlib.Path(__file__).parent.absolute())
        parameter_json_abs_path = current_dir_abs_path + "/all-parameters.json"
        data: str
        with open(parameter_json_abs_path, "r") as parameters_file:
            data = " ".join(parameters_file.readlines())

        return json.loads(data)["Parameters"]


if __name__ == "__main__":
    unittest.main()
