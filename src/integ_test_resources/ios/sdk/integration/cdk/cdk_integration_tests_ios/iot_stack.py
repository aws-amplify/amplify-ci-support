from aws_cdk import aws_iam, aws_lambda, core, custom_resources

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class IotStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region("iot")

        describe_endpoint_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["iot:DescribeEndpoint"], resources=["*"],
        )

        provider_lambda = aws_lambda.SingletonFunction(
            self,
            "iot-data-ats-endpoint-provider-lambda",
            uuid="iot-data-ats-endpoint-provider-lambda-20200507150213",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("custom_resources/iot_endpoint"),
            handler="iot_endpoint_provider.on_event",
            description="Returns iot:Data-ATS endpoint for this account",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.RETAIN
            ),
            initial_policy=[describe_endpoint_policy],
        )

        provider = custom_resources.Provider(
            self, "iot-data-ats-endpoint-provider", on_event_handler=provider_lambda
        )

        iot_endpoint = core.CustomResource(
            self,
            "iot-data-ats-endpoint",
            resource_type="Custom::IotDataAtsEndpoint",
            service_token=provider.service_token,
        )

        self._parameters_to_save = {
            "iot_endpoint_address": iot_endpoint.get_att("EndpointAddress").to_string()
        }
        self.save_parameters_in_parameter_store(platform=Platform.IOS)
