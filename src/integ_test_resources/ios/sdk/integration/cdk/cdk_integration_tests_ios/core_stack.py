from aws_cdk import(
    core,
    aws_cognito,
    aws_iam
)

from auth_utils import construct_identity_pool
from parameter_store import save_string_parameter


class CoreStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 circleci_execution_role: aws_iam.Role,
                 facebook_app_id: str,
                 facebook_app_secret: str,
                 **kwargs) -> None:

        super().__init__(scope,
                         id,
                         **kwargs)

        supported_login_providers = {
            "graph.facebook.com": facebook_app_id
        }

        (identity_pool_with_facebook,
         identity_pool_auth_role,
         identity_pool_unauth_role) = construct_identity_pool(self,
                                                              resource_id_prefix="core",
                                                              supported_login_providers=supported_login_providers,
                                                              developer_provider_name = "iostests.com"
                                                              )

        (unauth_identity_pool, _, _) = construct_identity_pool(self,
                                                               resource_id_prefix="core2",
                                                               auth_role=identity_pool_auth_role,
                                                               unauth_role=identity_pool_unauth_role
                                                              )

        wic_provider_test_role_condition = {
            "StringEquals": {
                "graph.facebook.com:app_id": facebook_app_id
            }
        }

        wic_provider_test_role = aws_iam.Role(self,
                                              "wic_provider_test_role",
                                              assumed_by=aws_iam.FederatedPrincipal("graph.facebook.com",
                                                                                    wic_provider_test_role_condition,
                                                                                    "sts:AssumeRoleWithWebIdentity")
                                              )
        wic_provider_test_role.add_to_policy(aws_iam.PolicyStatement(
                                                effect=aws_iam.Effect.ALLOW,
                                                actions=[
                                                    "translate:TranslateText",
                                                ],
                                                resources=["*"]
                                            ))

        save_string_parameter(self, "identityPoolId", identity_pool_with_facebook.ref)
        save_string_parameter(self, "unauthIdentityPoolId", unauth_identity_pool.ref)
        save_string_parameter(self, "authRoleArn", identity_pool_auth_role.role_arn)
        save_string_parameter(self, "unauthRoleArn", identity_pool_unauth_role.role_arn)
        save_string_parameter(self, "WICProviderTestRoleArn", wic_provider_test_role.role_arn)
        save_string_parameter(self, "facebookAppId", facebook_app_id)
        save_string_parameter(self, "facebookAppSecret", facebook_app_secret)

        circleci_execution_role.add_to_policy(aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                                                      actions=[
                                                                          "cognito-identity:*"],
                                                                      resources=["*"]
                                                                      ))

