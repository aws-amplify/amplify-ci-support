from aws_cdk import aws_iam, aws_iot, aws_lambda, core, custom_resources

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class IotStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region("iot")
        self._parameters_to_save = {}

        self.setup_custom_resource()
        self.setup_test_policies(common_stack)
        self.setup_iot_policy()

        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    def setup_custom_resource(self):
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

        endpoint_address_attribute = iot_endpoint.get_att("EndpointAddress")

        self._parameters_to_save["iot_endpoint_address"] = endpoint_address_attribute.to_string()

    def setup_test_policies(self, common_stack):
        specific_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["iot:AttachPrincipalPolicy"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:cert/*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=specific_resources_policy)

        all_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["iot:CreateCertificateFromCsr"], resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

    def setup_iot_policy(self):
        iot_policy = aws_iot.CfnPolicy(
            self,
            "iot-integ-test-policy",
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {"Effect": "Allow", "Action": "iot:Connect", "Resource": "*"},
                    {
                        "Effect": "Allow",
                        "Action": ["iot:Publish", "iot:Subscribe", "iot:Receive"],
                        "Resource": "*",
                    },
                ],
            },
            policy_name="iot-integ-test-policy",
        )
        self._parameters_to_save["iot_policy_name"] = iot_policy.policy_name
