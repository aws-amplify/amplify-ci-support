from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_lambda as lambda_
from constructs import Construct
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class ApigatewayStack(RegionAwareStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        lambda_echo: lambda_.Function,
        common_stack: CommonStack,
        **kwargs
    ) -> None:

        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        endpoint = apigateway.LambdaRestApi(self, "endpoint", handler=lambda_echo)

        self._parameters_to_save = {"endpointURL": endpoint.url}
        self.save_parameters_in_parameter_store(platform=Platform.IOS)

        common_stack.add_to_common_role_policies(self)
