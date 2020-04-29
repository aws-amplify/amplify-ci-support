from datetime import datetime

from aws_cdk import(
    core,
    aws_lambda,
    aws_iam
)
from parameter_store import save_string_parameter
from file_utils import replace_in_file
from common_stack import CommonStack
from cdk_stack_extension import CDKStackExtension

class LambdaStack(CDKStackExtension):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 common_stack: CommonStack,
                 **kwargs) -> None:

        super().__init__(scope,
                         id,
                         **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        echo = aws_lambda.Function(self,
                                   "echo",
                                   runtime=aws_lambda.Runtime.PYTHON_3_7,
                                   code=aws_lambda.Code.asset("lambda"),
                                   handler="echo.handler",
                                   description=datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                                   current_version_options=aws_lambda.VersionOptions(removal_policy=core.RemovalPolicy.RETAIN))

        self.attach_alias_to_version(echo.current_version, "Version2Alias")

        echo2 = aws_lambda.Function(self,
                                    "echo2",
                                    runtime=aws_lambda.Runtime.PYTHON_3_7,
                                    code=aws_lambda.Code.asset("lambda"),
                                    handler="echo.handler")

        save_string_parameter(self,
                              "echo_function_name",
                              echo.function_name)

        save_string_parameter(self,
                              "echo2_function_name",
                              echo2.function_name)

        self._lambda_echo_function = echo

        common_stack.add_to_common_role_policies(self)

    @property
    def lambda_echo_function(self) -> aws_lambda.IFunction:
        return self._lambda_echo_function

    @lambda_echo_function.setter
    def lambda_echo_function(self, value):
        self._lambda_echo_function = value

    def attach_alias_to_version(self, version_obj: aws_lambda.Version, alias: str):
        """
        Attach the given Alias to the given version of lambda
        """
        aws_lambda.Alias(self,
                         alias,
                         version=version_obj,
                         alias_name=alias)

    def create_version(self, lambda_function: aws_lambda.IFunction, version: str):
        ## MARK: this feature is deprecated and each stack deploy operation
        ## can create only a single version. We might have to deploy lambda stack twice
        ## to add version 2 that is required by the tests. See
        ## https://github.com/aws/aws-cdk/issues/5334
        ## https://github.com/aws/aws-cdk/commit/c94ce62bc71387d031cf291dbce40243feb50e83
        replace_in_file("lambda/echo.py",
                        r"ECHO_EVENT_VERSION = [0-9]*",
                        "ECHO_EVENT_VERSION = {}".format(version))

        current_version =  lambda_function.add_version(name=version)
        self.attach_alias_to_version(version_obj=current_version,
                                     alias="Version{}Alias".format(version))