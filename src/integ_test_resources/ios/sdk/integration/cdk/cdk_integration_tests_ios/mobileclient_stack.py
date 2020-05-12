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

        user_pool = aws_cognito.UserPool(
            self,
            "userpool",
            required_attributes=aws_cognito.RequiredAttributes(email=True),
            self_sign_up_enabled=True,
            auto_verify=aws_cognito.AutoVerifiedAttrs(email=True),
        )

        user_pool_client = aws_cognito.CfnUserPoolClient(
            self, "userpool_client", generate_secret=True, user_pool_id=user_pool.user_pool_id
        )

        user_pool_client_secret = self.create_userpool_client_secret_custom_resource(
            user_pool, user_pool_client
        )

        (identity_pool, _, _) = construct_identity_pool(
            self,
            resource_id_prefix="mobileclient",
            cognito_identity_providers=[
                {
                    "clientId": user_pool_client.ref,
                    "providerName": user_pool.user_pool_provider_name,
                }
            ],
        )

        stack_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["cognito-identity:*"], resources=["*"]
        )

        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)

        self._parameters_to_save = {
            "userpool_id": user_pool.user_pool_id,
            "pool_id_dev_auth": identity_pool.ref,
            "email_address": "aws-mobile-sdk-dev+mc-integ-tests@amazon.com",
        }

        self.update_parameters_for_userpool(user_pool, user_pool_client, user_pool_client_secret)

        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    def create_userpool_client_secret_custom_resource(
        self, user_pool, user_pool_client
    ) -> custom_resources.AwsCustomResource:
        """
        :return: an AwsCustomResource that provides access to the user pool client secret in the
            response field `user_pool_client_secret`
        """
        resource = custom_resources.AwsCustomResource(
            self,
            "userpool_client_secret_custom_resource",
            resource_type="Custom::UserPoolClientSecret",
            policy=custom_resources.AwsCustomResourcePolicy.from_statements(
                [
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.ALLOW,
                        actions=["cognito-idp:DescribeUserPoolClient"],
                        resources=[
                            f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{user_pool.user_pool_id}"  # noqa: E501
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

    def update_parameters_for_userpool(self, user_pool, user_pool_client, user_pool_client_secret):
        self._parameters_to_save.update(
            {
                "CognitoUserPool/Default/PoolId": user_pool.user_pool_id,
                "CognitoUserPool/Default/AppClientId": user_pool_client.ref,
                "CognitoUserPool/Default/AppClientSecret": user_pool_client_secret.get_response_field(  # noqa: E501
                    "UserPoolClient.ClientSecret"
                ),
            }
        )
