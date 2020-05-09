from aws_cdk import aws_lambda, core

from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack


class LambdaStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.are_services_supported_in_region(["lambda"])

        aws_lambda.Function(
            self,
            "EchoHandler",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("lambda"),
            handler="echo_handler.handler",
            function_name="echo",
        )

        echo_first = aws_lambda.Function(
            self,
            "EchoFirstHandler",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("lambda"),
            handler="echo_handler_first.handler",
            function_name="echoFirst",
        )

        echo_first.add_version("1")

        aws_lambda.Alias(self, "alias", alias_name="alias", version=echo_first.latest_version)

        common_stack.add_to_common_role_policies(self)
