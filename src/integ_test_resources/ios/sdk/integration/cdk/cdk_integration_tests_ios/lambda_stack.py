from datetime import datetime

from aws_cdk import aws_lambda, core

from common.common_stack import CommonStack
from common.file_utils import replace_in_file
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class LambdaStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:

        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        echo = aws_lambda.Function(
            self,
            "echo",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("lambda"),
            handler="echo.handler",
            description=datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"),
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.RETAIN
            ),
        )

        version_alias_associated_version, version_alias_name = self.attach_alias_to_version(echo.current_version)

        echo2 = aws_lambda.Function(
            self,
            "echo2",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("lambda"),
            handler="echo.handler",
        )

        self._parameters_to_save = {
            "echo_function_name": echo.function_name,
            "echo2_function_name": echo2.function_name,
            "version_alias_name": version_alias_name,
            "version_alias_associated_version": version_alias_associated_version,
        }
        self.save_parameters_in_parameter_store(platform=Platform.IOS)

        self._lambda_echo_function = echo

        common_stack.add_to_common_role_policies(self)

    @property
    def lambda_echo_function(self) -> aws_lambda.IFunction:
        return self._lambda_echo_function

    @lambda_echo_function.setter
    def lambda_echo_function(self, value):
        self._lambda_echo_function = value

    def attach_alias_to_version(self, version_obj: aws_lambda.Version) -> (str, str):
        """
        Creates a version alias for the given version of the lambda

        :return: The version alias string
        """
        version_alias_associated_version = version_obj.version
        version_alias_name = "integ_test_current_version_alias"
        aws_lambda.Alias(
            self,
            "integ_test_lambda_current_version_alias",
            version=version_obj,
            alias_name=version_alias_name
        )
        return version_alias_associated_version, version_alias_name

    def create_version(self, lambda_function: aws_lambda.IFunction, version: str):
        # MARK: this feature is deprecated and each stack deploy operation
        # can create only a single version. We might have to deploy lambda stack twice
        # to add version 2 that is required by the tests. See
        # https://github.com/aws/aws-cdk/issues/5334
        # https://github.com/aws/aws-cdk/commit/c94ce62bc71387d031cf291dbce40243feb50e83
        replace_in_file(
            "lambda/echo.py",
            r"ECHO_EVENT_VERSION = [0-9]*",
            "ECHO_EVENT_VERSION = {}".format(version),
        )

        current_version = lambda_function.add_version(name=version)
        self.attach_alias_to_version(
            version_obj=current_version, alias="Version{}Alias".format(version)
        )
