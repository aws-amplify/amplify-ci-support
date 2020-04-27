from aws_cdk import(
    core,
    aws_cognito,
    aws_iam
)

from auth_utils import construct_identity_pool
from parameter_store import string_parameter


class CoreStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 circleci_execution_role: aws_iam.Role,
                 **kwargs) -> None:

        super().__init__(scope,
                         id,
                         **kwargs)

        ## TODO:: Move to Secrets Manager and fetch inside the tests
        ## Blocker:: Need Secrets Manager iOS SDK
        FACEBOOK_APP_ID = "336035153157769"
        FACEBOOK_APP_SECRET = "f5763dd3ca920305dadb7e1f794926e8"
        supported_login_providers = {
            "graph.facebook.com": FACEBOOK_APP_ID
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
                "graph.facebook.com:app_id": FACEBOOK_APP_ID
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

        string_parameter(self, "identityPoolId", identity_pool_with_facebook.ref)
        string_parameter(self, "unauthIdentityPoolId", unauth_identity_pool.ref)
        string_parameter(self, "authRoleArn", identity_pool_auth_role.role_arn)
        string_parameter(self, "unauthRoleArn", identity_pool_unauth_role.role_arn)
        string_parameter(self, "WICProviderTestRoleArn", wic_provider_test_role.role_arn)
        string_parameter(self, "facebookAppId", FACEBOOK_APP_ID)
        string_parameter(self, "facebookAppSecret", FACEBOOK_APP_SECRET)

        circleci_execution_role.add_to_policy(aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                                                      actions=[
                                                                          "cognito-identity:*"],
                                                                      resources=["*"]
                                                                      ))

