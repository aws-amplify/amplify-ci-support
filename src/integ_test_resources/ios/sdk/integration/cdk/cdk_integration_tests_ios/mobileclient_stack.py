from aws_cdk import aws_cognito, aws_iam, core, custom_resources

from common.auth_utils import construct_identity_pool
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class MobileClientStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:

        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.are_services_supported_in_region(
            ["cognito-identity", "cognito-idp"]
        )

        self.update_common_stack_with_test_policy(common_stack)

        default_user_pool = self.create_user_pool("default")
        default_user_pool_client = self.create_user_pool_client(default_user_pool, "default")
        default_user_pool_client_secret = self.create_userpool_client_secret(
            default_user_pool, default_user_pool_client, "default"
        )
        self.update_parameters_for_userpool(
            default_user_pool, default_user_pool_client, default_user_pool_client_secret, "Default"
        )

        (identity_pool, _, _) = construct_identity_pool(
            self,
            resource_id_prefix="mobileclient",
            cognito_identity_providers=[
                {
                    "clientId": default_user_pool_client.ref,
                    "providerName": default_user_pool.user_pool_provider_name,
                }
            ],
        )
        self.update_parameters_for_identity_pool(identity_pool)

        custom_auth_user_pool = self.create_user_pool("custom_auth")
        custom_auth_user_pool_client = self.create_user_pool_client(
            custom_auth_user_pool, "custom_auth"
        )
        custom_auth_user_pool_client_secret = self.create_userpool_client_secret(
            custom_auth_user_pool, custom_auth_user_pool_client, "custom_auth"
        )
        self.update_parameters_for_userpool(
            custom_auth_user_pool,
            custom_auth_user_pool_client,
            custom_auth_user_pool_client_secret,
            "DefaultCustomAuth",
        )

        self._parameters_to_save["email_address"] = "aws-mobile-sdk-dev+mc-integ-tests@amazon.com"
        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    def create_user_pool(self, tag) -> aws_cognito.UserPool:
        user_pool = aws_cognito.UserPool(
            self,
            f"userpool_{tag}",
            required_attributes=aws_cognito.RequiredAttributes(email=True),
            self_sign_up_enabled=True,
            auto_verify=aws_cognito.AutoVerifiedAttrs(email=True),
        )
        return user_pool

    def create_user_pool_client(self, user_pool, tag) -> aws_cognito.CfnUserPoolClient:
        user_pool_client = aws_cognito.CfnUserPoolClient(
            self,
            f"userpool_client_{tag}",
            generate_secret=True,
            user_pool_id=user_pool.user_pool_id,
        )
        return user_pool_client

    def create_userpool_client_secret(
        self, user_pool, user_pool_client, tag
    ) -> custom_resources.AwsCustomResource:
        """
        :return: an AwsCustomResource that provides access to the user pool client secret in the
            response field `user_pool_client_secret`
        """
        resource = custom_resources.AwsCustomResource(
            self,
            f"userpool_client_secret_{tag}",
            resource_type="Custom::UserPoolClientSecret",
            policy=custom_resources.AwsCustomResourcePolicy.from_statements(
                [
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.ALLOW,
                        actions=["cognito-idp:DescribeUserPoolClient"],
                        resources=[
                            f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{user_pool.user_pool_id}"
                            # noqa: E501
                        ],
                    )
                ]
            ),
            on_create=custom_resources.AwsSdkCall(
                physical_resource_id=custom_resources.PhysicalResourceId.of(user_pool_client.ref),
                service="CognitoIdentityServiceProvider",
                action="describeUserPoolClient",
                output_path="UserPoolClient.ClientSecret",
                parameters={"ClientId": user_pool_client.ref, "UserPoolId": user_pool.user_pool_id},
            ),
            on_update=custom_resources.AwsSdkCall(
                physical_resource_id=custom_resources.PhysicalResourceId.of(user_pool_client.ref),
                service="CognitoIdentityServiceProvider",
                action="describeUserPoolClient",
                output_path="UserPoolClient.ClientSecret",
                parameters={"ClientId": user_pool_client.ref, "UserPoolId": user_pool.user_pool_id},
            ),
        )
        return resource

    def update_common_stack_with_test_policy(self, common_stack):
        stack_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["cognito-identity:*"], resources=["*"]
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)

    def update_parameters_for_identity_pool(self, identity_pool):
        self._parameters_to_save.update(
            {
                "awsconfiguration/CredentialsProvider/CognitoIdentity/Default/PoolId": identity_pool.ref,  # noqa: E501
                "awsconfiguration/CredentialsProvider/CognitoIdentity/Default/Region": self.region,
            }
        )

    def update_parameters_for_userpool(
        self, user_pool, user_pool_client, user_pool_client_secret, tag
    ):
        self._parameters_to_save.update(
            {
                f"awsconfiguration/CognitoUserPool/{tag}/PoolId": user_pool.user_pool_id,
                f"awsconfiguration/CognitoUserPool/{tag}/AppClientId": user_pool_client.ref,
                f"awsconfiguration/CognitoUserPool/{tag}/AppClientSecret": user_pool_client_secret.get_response_field(  # noqa: E501
                    "UserPoolClient.ClientSecret"
                ),
                f"awsconfiguration/CognitoUserPool/{tag}/Region": self.region,
            }
        )
