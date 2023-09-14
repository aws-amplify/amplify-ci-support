import hashlib
import json
from aws_cdk import aws_iam as iam
from aws_cdk import aws_iot as iot
from aws_cdk import aws_lambda as lambda_
from aws_cdk import custom_resources as custom_resources
from aws_cdk import CustomResource, RemovalPolicy
from constructs import Construct
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class IotStack(RegionAwareStack):
    custom_auth_user_pass_username = "aws-sdk-user"
    custom_auth_user_pass_password = "%%aws-sdk-password**"
    custom_auth_user_pass_uuid = "iot_custom_authorizer_provider_lambda_20200507150213"
    custom_auth_user_pass_default_authorizer_name = "iot_custom_authorizer_user_pass"
    custom_auth_user_pass_domain_configuration_name = "aws_test_iot_custom_authorizer_user_pass"

    def __init__(self, scope: Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region("iot")
        self._parameters_to_save = {}

        self.setup_test_policies(common_stack)
        self.setup_iot_policy()

        # Set up custom resources
        self.setup_iot_endpoint_provider()
        self.setup_custom_authorizer()

        self.setup_custom_authorizer_user_pass()

        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    def setup_iot_endpoint_provider(self):
        describe_endpoint_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:DescribeEndpoint"],
            resources=["*"],
        )

        provider_lambda = lambda_.SingletonFunction(
            self,
            "iot_data_ats_endpoint_provider_lambda",
            uuid="iot_data_ats_endpoint_provider_lambda_20200507150213",
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.AssetCode.from_asset("custom_resources/iot_endpoint"),
            handler="iot_endpoint_provider.on_event",
            description="Returns iot:Data-ATS endpoint for this account",
            current_version_options=lambda_.VersionOptions(
                removal_policy=RemovalPolicy.DESTROY
            ),
            initial_policy=[describe_endpoint_policy],
        )

        provider = custom_resources.Provider(
            self, "iot_data_ats_endpoint_provider", on_event_handler=provider_lambda
        )

        iot_endpoint = CustomResource(
            self,
            "iot_data_ats_endpoint",
            resource_type="Custom::IotDataAtsEndpoint",
            service_token=provider.service_token,
        )

        endpoint_address = iot_endpoint.get_att("EndpointAddress").to_string()

        self._parameters_to_save["iot_endpoint_address"] = endpoint_address

    def setup_test_policies(self, common_stack):
        cert_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:AttachPrincipalPolicy"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:cert/*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=cert_policy)

        client_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:Connect"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:client*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=client_policy)

        thing_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:DeleteThingShadow", "iot:GetThingShadow", "iot:UpdateThingShadow"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:thing*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=thing_policy)

        topic_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:Publish", "iot:Receive"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:topic*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=topic_policy)

        topicfilter_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:Subscribe"],
            resources=[f"arn:aws:iot:{self.region}:{self.account}:topicfilter*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=topicfilter_policy)

        all_resources_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:CreateCertificateFromCsr"],
            resources=["*"],
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

        iot.CfnPolicy(
            self,
            "iot_integ_test_policy",
            policy_document=policy_document,
            policy_name=policy_name,
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

        iot_custom_authorizer_key_resource = self.create_custom_authorizer_signing_key_generic(
            "1",
            "Manages an asymmetric CMK and token signature for iot custom authorizer.",
            token_value,
        )

        custom_authorizer_token_signature = iot_custom_authorizer_key_resource.get_att(
            "custom_authorizer_token_signature"
        ).to_string()
        self._parameters_to_save[
            "custom_authorizer_token_signature"
        ] = custom_authorizer_token_signature

        authorizer_function_arn = self.setup_custom_authorizer_function(
            "1",
            "custom_resources/iot_custom_authorizer_function",
            "iot_custom_authorizer.handler",
            "Sample custom authorizer that allows or denies based on 'token' value",
            {},
            self.region,
        )

        create_authorizer_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:CreateAuthorizer", "iot:UpdateAuthorizer", "iot:DeleteAuthorizer"],
            resources=["*"],
        )
        provider_lambda = lambda_.SingletonFunction(
            self,
            "iot_custom_authorizer_provider_lambda",
            uuid=self.custom_auth_user_pass_uuid,
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.AssetCode.from_asset("custom_resources/iot_custom_authorizer_provider"),
            handler="iot_custom_authorizer_provider.on_event",
            description="Sets up an IoT custom authorizer",
            current_version_options=lambda_.VersionOptions(
                removal_policy=RemovalPolicy.DESTROY
            ),
            initial_policy=[create_authorizer_policy],
        )

        provider = custom_resources.Provider(
            self, "iot_custom_authorizer_provider", on_event_handler=provider_lambda
        )

        public_key = iot_custom_authorizer_key_resource.get_att(
            "custom_authorizer_public_key"
        ).to_string()

        CustomResource(
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

    def setup_custom_authorizer_user_pass(self):
        custom_authorizer_name = self.custom_auth_user_pass_default_authorizer_name
        self._parameters_to_save["custom_authorizer_user_pass_name"] = custom_authorizer_name
        token_key_name = "IoTTokenKeyName"
        self._parameters_to_save["custom_authorizer_user_pass_token_key_name"] = token_key_name
        token_value = "allow"
        self._parameters_to_save["custom_authorizer_user_pass_token_value"] = token_value
        self._parameters_to_save[
            "custom_authorizer_user_pass_username"
        ] = self.custom_auth_user_pass_username
        self._parameters_to_save[
            "custom_authorizer_user_pass_password"
        ] = self.custom_auth_user_pass_password

        iot_custom_authorizer_key_resource = self.create_custom_authorizer_signing_key_generic(
            "2",
            "Manages an asymmetric CMK and token signature for iot custom authorizer with "
            "username and password.",
            token_value,
        )

        custom_authorizer_token_signature = iot_custom_authorizer_key_resource.get_att(
            "custom_authorizer_token_signature"
        ).to_string()
        self._parameters_to_save[
            "custom_authorizer_user_pass_token_signature"
        ] = custom_authorizer_token_signature

        # Force region to 'us-east-1' due to enhanced custom authorizers only available there
        # TODO: remove override when enhanced custom authorizers are available in all regions
        authorizer_function_arn = self.setup_custom_authorizer_function(
            "2",
            "custom_resources/iot_custom_authorizer_user_pass_function",
            "iot_custom_authorizer_user_pass.handler",
            "Sample custom authorizer that allows or denies based on username and password",
            {
                "custom_auth_user_pass_username": self.custom_auth_user_pass_username,
                "custom_auth_user_pass_password": self.custom_auth_user_pass_password,
            },
            "us-east-1",
        )
        create_authorizer_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "iot:CreateAuthorizer",
                "iot:UpdateAuthorizer",
                "iot:DeleteAuthorizer",
                "iot:UpdateDomainConfiguration",
                "iot:CreateDomainConfiguration",
                "iot:DescribeDomainConfiguration",
                "iot:DeleteDomainConfiguration",
            ],
            resources=["*"],
        )
        provider_lambda = lambda_.SingletonFunction(
            self,
            "iot_custom_authorizer_user_pass_provider_lambda",
            uuid="iot_custom_authorizer_user_pass_provider_lambda_20200727123737",
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.AssetCode.from_asset("custom_resources/iot_custom_authorizer_user_pass_provider"),
            handler="iot_custom_authorizer_user_pass_provider.on_event",
            description="Sets up an IoT custom authorizer for user password & required domain "
            "config due to beta status",
            environment={
                "custom_auth_user_pass_uuid": self.custom_auth_user_pass_uuid,
                "custom_auth_user_pass_default_authorizer_name": (
                    self.custom_auth_user_pass_default_authorizer_name
                ),
                "custom_auth_user_pass_domain_configuration_name": (
                    self.custom_auth_user_pass_domain_configuration_name
                ),
            },
            current_version_options=lambda_.VersionOptions(
                removal_policy=RemovalPolicy.DESTROY
            ),
            initial_policy=[create_authorizer_policy],
        )

        provider = custom_resources.Provider(
            self, "iot_custom_authorizer_user_pass_provider", on_event_handler=provider_lambda
        )

        public_key = iot_custom_authorizer_key_resource.get_att(
            "custom_authorizer_public_key"
        ).to_string()

        iot_endpoint = CustomResource(
            self,
            "iot_custom_authorizer_user_pass",
            resource_type="Custom::IoTCustomAuthorizer",
            service_token=provider.service_token,
            properties={
                "authorizer_function_arn": authorizer_function_arn,
                "authorizer_name": custom_authorizer_name,
                "public_key": public_key,
                "token_key_name": token_key_name,
            },
        )
        endpoint_address = iot_endpoint.get_att("BetaEndpointAddress").to_string()
        self._parameters_to_save["iot_beta_endpoint_address"] = endpoint_address

    def setup_custom_authorizer_function(
        self, unique_id, code_asset, code_handler, description, environment, region
    ) -> str:
        """
        Sets up the authorizer Lambda, and grants 'lambda:InvokeFunction' to the service principal
        'iot.amazonaws.com'

        :return: the ARN of the created function
        """
        merged_environment_vars = {"RESOURCE_ARN": f"arn:aws:iot:{region}:{self.account}:*"}
        merged_environment_vars.update(environment)
        authorizer_function = lambda_.Function(
            self,
            f"iot_custom_authorizer_function_{unique_id}",
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.AssetCode.from_asset(code_asset),
            handler=code_handler,
            description=description,
            current_version_options=lambda_.VersionOptions(
                removal_policy=RemovalPolicy.DESTROY
            ),
            environment=merged_environment_vars,
        )

        authorizer_function.grant_invoke(iam.ServicePrincipal("iot.amazonaws.com"))
        return authorizer_function.function_arn

    def create_custom_authorizer_signing_key_generic(
        self, unique_id, description, token_value
    ) -> CustomResource:
        """
        Uses a Lambda to create an asymmetric key pair, since neither CFn nor CDK support that as of
        this writing (2020-05-09)
        https://github.com/aws-cloudformation/aws-cloudformation-coverage-roadmap/issues/337

        After creating the key, it signs the token value using the private key, and stores all of
        `token_value`, `token_value`'s signature, and the public key in the stack's parameter store.

        :return: the CustomResource for the signing key
        """
        create_authorizer_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["kms:CreateKey", "kms:GetPublicKey", "kms:ScheduleKeyDeletion", "kms:Sign"],
            resources=["*"],
        )
        provider_lambda = lambda_.SingletonFunction(
            self,
            f"iot_custom_authorizer_key_provider_lambda_{unique_id}",
            uuid=f"iot_custom_authorizer_key_provider_lambda_20200507150213_{unique_id}",
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.AssetCode.from_asset("custom_resources/iot_custom_authorizer_key_provider"),
            handler="iot_custom_authorizer_key_provider.on_event",
            description=description,
            current_version_options=lambda_.VersionOptions(
                removal_policy=RemovalPolicy.DESTROY
            ),
            initial_policy=[create_authorizer_policy],
        )

        provider = custom_resources.Provider(
            self,
            f"iot_custom_authorizer_key_provider_{unique_id}",
            on_event_handler=provider_lambda,
        )

        iot_custom_authorizer_key = CustomResource(
            self,
            f"iot_custom_authorizer_key_{unique_id}",
            resource_type="Custom::IoTCustomAuthorizer",
            service_token=provider.service_token,
            properties={"token_value": token_value},
        )

        return iot_custom_authorizer_key
