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
            "iot_data_ats_endpoint_provider_lambda",
            uuid="iot_data_ats_endpoint_provider_lambda_20200507150213",
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
            self, "iot_data_ats_endpoint_provider", on_event_handler=provider_lambda
        )

        iot_endpoint = core.CustomResource(
            self,
            "iot_data_ats_endpoint",
            resource_type="Custom::IotDataAtsEndpoint",
            service_token=provider.service_token,
        )

        endpoint_address = iot_endpoint.get_att("EndpointAddress").to_string()

        self._parameters_to_save["iot_endpoint_address"] = endpoint_address

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
        policy_name = f"iot_integ_test_policy_{md5_hash}"

        aws_iot.CfnPolicy(
            self, "iot_integ_test_policy", policy_document=policy_document, policy_name=policy_name,
        )
        self._parameters_to_save["policy_name"] = policy_name

    def setup_custom_authorizer(self):
        # These values are used in the custom authorizer setup, and exported to Parameter Store
        # for use by integration tests
        custom_authorizer_name = "iot_custom_authorizer"
        self._parameters_to_save["custom_authorizer_name"] = custom_authorizer_name

        # Note: "key" is a bit overloaded here. In the context of the custom authorizer, "key name"
        # refers to the HTTP header field that the custom authorizer looks for a token value in.
        #
        # In the case of the custom authorizer key provider, the "key" is the KMS asymmetric CMK
        # used to sign the token value passed in the `token_key_name` header. In order to keep the
        # terminology consistent between client integ tests that are expecting to pass something for
        # a "key name" field, we'll let the ambiguity stand.
        token_key_name = "iot_custom_authorizer_token"
        self._parameters_to_save["custom_authorizer_token_key_name"] = token_key_name

        token_value = "allow"
        self._parameters_to_save["custom_authorizer_token_value"] = token_value

        iot_custom_authorizer_key_resource = self.create_custom_authorizer_signing_key(token_value)

        custom_authorizer_token_signature = iot_custom_authorizer_key_resource.get_att(
            "custom_authorizer_token_signature"
        ).to_string()
        self._parameters_to_save[
            "custom_authorizer_token_signature"
        ] = custom_authorizer_token_signature

        authorizer_function_arn = self.setup_custom_authorizer_function()

        create_authorizer_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["iot:CreateAuthorizer"], resources=["*"],
        )
        provider_lambda = aws_lambda.SingletonFunction(
            self,
            "iot_custom_authorizer_provider_lambda",
            uuid="iot_custom_authorizer_provider_lambda_20200507150213",
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
            self, "iot_custom_authorizer_provider", on_event_handler=provider_lambda
        )

        public_key = iot_custom_authorizer_key_resource.get_att(
            "custom_authorizer_public_key"
        ).to_string()

        core.CustomResource(
            self,
            "iot_custom_authorizer",
            resource_type="Custom::IoTCustomAuthorizer",
            service_token=provider.service_token,
            properties={
                "authorizer_function_arn": authorizer_function_arn,
                "authorizer_name": custom_authorizer_name,
                "public_key": public_key,
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
            "iot_custom_authorizer_function",
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

    def create_custom_authorizer_signing_key(self, token_value) -> core.CustomResource:
        """
        Uses a Lambda to create an asymmetric key pair, since neither CFn nor CDK support that as of
        this writing (2020-05-09)
        https://github.com/aws-cloudformation/aws-cloudformation-coverage-roadmap/issues/337

        After creating the key, it signs the token value using the private key, and stores all of
        `token_value`, `token_value`'s signature, and the public key in the stack's parameter store.

        :return: the CustomResource for the signing key
        """
        create_authorizer_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["kms:CreateKey", "kms:GetPublicKey", "kms:ScheduleKeyDeletion", "kms:Sign"],
            resources=["*"],
        )
        provider_lambda = aws_lambda.SingletonFunction(
            self,
            "iot_custom_authorizer_key_provider_lambda",
            uuid="iot_custom_authorizer_key_provider_lambda_20200507150213",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("custom_resources/iot_custom_authorizer_key_provider"),
            handler="iot_custom_authorizer_key_provider.on_event",
            description="Manages an asymmetric CMK and token signature for iot custom authorizer.",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.RETAIN
            ),
            initial_policy=[create_authorizer_policy],
        )

        provider = custom_resources.Provider(
            self, "iot_custom_authorizer_key_provider", on_event_handler=provider_lambda
        )

        iot_custom_authorizer_key = core.CustomResource(
            self,
            "iot_custom_authorizer_key",
            resource_type="Custom::IoTCustomAuthorizer",
            service_token=provider.service_token,
            properties={"token_value": token_value},
        )

        return iot_custom_authorizer_key
