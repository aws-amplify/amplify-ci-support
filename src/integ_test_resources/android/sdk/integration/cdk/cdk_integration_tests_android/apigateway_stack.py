import random

from aws_cdk import aws_apigateway as apigateway
from aws_cdk import core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class ApiGatewayStack(RegionAwareStack):
    HTTPBIN_URL_TEMPLATE = "http://httpbin.org/{method}"
    ENDPOINT = "https://{id}.execute-api.us-east-2.amazonaws.com/prod"

    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        # Create API
        api = apigateway.RestApi(self, "testApi")

        # Generate a random API key, add it to the underlying CloudFormation
        # resource of the Construct so that we can use it in our tests.
        api_key_value = self.random_hex(20)
        api_key = api.add_api_key("testKey")
        cfn_api_key = api_key.node.default_child
        cfn_api_key.add_property_override("Value", api_key_value)

        # Create Usage Plan and add it to the API
        plan = api.add_usage_plan("usagePlan", api_key=api_key)
        plan.add_api_stage(stage=api.deployment_stage)

        # Create resources in API
        echo = api.root.add_resource("echo")
        echo_post = echo.add_resource("post")
        auth = api.root.add_resource("auth")
        apikey = api.root.add_resource("apikey")

        # Wire up methods
        get_url = self.HTTPBIN_URL_TEMPLATE.format(method="get")
        post_url = self.HTTPBIN_URL_TEMPLATE.format(method="post")

        get_integration = apigateway.HttpIntegration(get_url)
        post_integration = apigateway.HttpIntegration(post_url, http_method="POST")
        options_integration = apigateway.HttpIntegration(get_url, http_method="OPTIONS")
        head_integration = apigateway.HttpIntegration(get_url, http_method="HEAD")

        echo.add_method("GET", get_integration)
        echo.add_method("OPTIONS", options_integration)
        echo.add_method("HEAD", head_integration)
        echo_post.add_method("POST", post_integration)
        auth.add_method("GET", get_integration, authorization_type=apigateway.AuthorizationType.IAM)
        apikey.add_method("GET", get_integration, api_key_required=True)

        # Generate all methods for /echo
        for method in ("put", "post", "delete", "patch"):
            url = self.HTTPBIN_URL_TEMPLATE.format(method=method)
            integration = apigateway.HttpIntegration(url, http_method=method)
            echo.add_method(method.upper(), integration)

        # Create SSM parameters for the endpoint of the API and the API key

        self._parameters_to_save = {"endpoint": api.url, "api_key": api_key_value}
        self.save_parameters_in_parameter_store(platform=Platform.ANDROID)

        common_stack.add_to_common_role_policies(self)

    def random_hex(self, length):
        rand = "%x" % random.randrange(10 ** 80)
        return rand[:length]
