import hashlib
import json

from aws_cdk import aws_iam, aws_iot, aws_lambda, core, custom_resources

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class IotStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region("iot")
        self._parameters_to_save = {}

        self.setup_test_policies(common_stack)
        self.setup_iot_policy()

        # Set up custom resources
        self.setup_iot_endpoint_provider()
        self.setup_custom_authorizer()

        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    def setup_iot_endpoint_provider(self):
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
        cert_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["iot:AttachPrincipalPolicy"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:cert/*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=cert_policy)

        client_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["iot:Connect"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:client*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=client_policy)

        thing_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["iot:DeleteThingShadow", "iot:GetThingShadow", "iot:UpdateThingShadow"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:thing*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=thing_policy)

        topic_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["iot:Publish", "iot:Receive"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:topic*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=topic_policy)

        topicfilter_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["iot:Subscribe"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:topicfilter*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=topicfilter_policy)

        all_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["iot:CreateCertificateFromCsr"], resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

    def setup_iot_policy(self):
        """
        Sets up an IoT Policy to be granted to Things that are authenticated during tests. This
        policy isn't an IAM policy assigned to normal IAM principals; it's an IoT policy attached
        to IoT Things.

        An IoT policy cannot be statically named or it will fail during update if there are any
        principals attached to it (e.g., certificates). A dynamic string has the benefit of allowing
        updates to the policy, but the downsides of a) failing to delete the old policy, which
        results in a longer deployment time while the delete retries for several minutes; and b) old
        policies cluttering the test account.

        We compromise below by naming the policy with the hash of the policy document itself. That
        ensures that updates are applied to a newly-named policy, while avoiding the overhead of
        updating a policy every time we deploy.
        """

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["iot:Connect", "iot:Publish", "iot:Subscribe", "iot:Receive"],
                    "Resource": f"arn:aws:iot:{self.region}:{self.account}:*",
                },
            ],
        }

        policy_string = json.dumps(policy_document)
        policy_bytes = bytes(policy_string, "utf8")
        md5_hash = hashlib.md5(policy_bytes).hexdigest()
        policy_name = f"iot-integ-test-policy-{md5_hash}"

        aws_iot.CfnPolicy(
            self, "iot-integ-test-policy", policy_document=policy_document, policy_name=policy_name,
        )
        self._parameters_to_save["policy_name"] = policy_name

    def setup_custom_authorizer(self):
        # These values are used in the custom authorizer setup, and exported to Parameter Store
        # for use by integration tests
        custom_authorizer_name = "iot_custom_authorizer"
        token_key_name = "iot-custom-authorizer-token"
        token_value = "allow"
        token_signature = IotStack.get_token_signature()

        self._parameters_to_save["custom_authorizer_name"] = custom_authorizer_name
        self._parameters_to_save["custom_authorizer_token_signature"] = token_signature
        self._parameters_to_save["custom_authorizer_token_key_name"] = token_key_name
        self._parameters_to_save["custom_authorizer_token_value"] = token_value

        authorizer_function_arn = self.setup_custom_authorizer_function()

        create_authorizer_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["iot:CreateAuthorizer"], resources=["*"],
        )
        provider_lambda = aws_lambda.SingletonFunction(
            self,
            "iot-custom-authorizer-provider-lambda",
            uuid="iot-custom-authorizer-provider-lambda-20200507150213",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("custom_resources/iot_custom_authorizer_provider"),
            handler="iot_custom_authorizer_provider.on_event",
            description="Sets up an IoT custom authorizer",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.RETAIN
            ),
            initial_policy=[create_authorizer_policy],
        )

        provider = custom_resources.Provider(
            self, "iot-custom-authorizer-provider", on_event_handler=provider_lambda
        )

        core.CustomResource(
            self,
            "iot-custom-authorizer",
            resource_type="Custom::IoTCustomAuthorizer",
            service_token=provider.service_token,
            properties={
                "authorizer_arn": authorizer_function_arn,
                "authorizer_name": custom_authorizer_name,
                "public_key": IotStack.get_public_key(),
                "token_key_name": token_key_name,
            },
        )

    def setup_custom_authorizer_function(self) -> str:
        """
        Sets up the authorizer Lambda, and grants 'lambda:InvokeFunction' to the service principal
        'iot.amazonaws.com'

        :return: the ARN of the created function
        """
        authorizer_function = aws_lambda.Function(
            self,
            "iot-custom-authorizer-function",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("custom_resources/iot_custom_authorizer_function"),
            handler="iot_custom_authorizer.handler",
            description="Sample custom authorizer that allows or denies based on 'token' value",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.RETAIN
            ),
            environment={"RESOURCE_ARN": f"arn:aws:iot:{self.region}:{self.account}:*"},
        )
        authorizer_function.grant_invoke(aws_iam.ServicePrincipal("iot.amazonaws.com"))
        return authorizer_function.function_arn

    @staticmethod
    def get_public_key():
        public_key: str
        with open(
            "custom_resources/iot_custom_authorizer_provider/iot_custom_authorizer_public.pem"
        ) as f:
            public_key = f.read()
        return public_key

    @staticmethod
    def get_token_signature():
        signature: str
        with open("custom_resources/iot_custom_authorizer_provider/token_signature.base64") as f:
            signature = f.read()
        return signature
