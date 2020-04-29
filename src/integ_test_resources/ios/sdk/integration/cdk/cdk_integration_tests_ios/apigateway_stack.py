from aws_cdk import(
    core,
    aws_lambda,
    aws_apigateway,
    aws_cloudformation,
    aws_iam
)
from parameter_store import save_string_parameter
from common_stack import CommonStack
from cdk_stack_extension import CDKStackExtension


class ApigatewayStack(CDKStackExtension):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 lambda_echo: aws_lambda.Function,
                 common_stack: CommonStack,
                 **kwargs) -> None:

        super().__init__(scope,
                         id,
                         **kwargs)

        self._supported_in_region = self.is_service_supported_in_region("apigateway")

        endpoint = aws_apigateway.LambdaRestApi(self,
                                                "endpoint",
                                                handler=lambda_echo)
        save_string_parameter(self,
                              "endpointURL",
                              endpoint.url)

        common_stack.add_to_common_role_policies(self)
