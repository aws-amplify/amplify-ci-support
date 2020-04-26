from aws_cdk import(
    core,
    aws_cloudformation,
    aws_cognito,
    aws_iam
)
from parameter_store import string_parameter


class MobileclientStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 circleci_execution_role: aws_iam.Role,
                 **kwargs) -> None:

        super().__init__(scope,
                         id,
                         **kwargs)
        self.stackId = id

        user_pool = aws_cognito.UserPool(self,
                                         "mobileclient_userpool",
                                         required_attributes=aws_cognito.RequiredAttributes(email=True),
                                         self_sign_up_enabled=True,
                                         auto_verify=aws_cognito.AutoVerifiedAttrs(email=True))

        user_pool_client = aws_cognito.UserPoolClient(self,
                                                      "mobileclient_userpool_client",
                                                      generate_secret=False,
                                                      user_pool=user_pool)

        identity_pool = aws_cognito.CfnIdentityPool(self,
                                                    "mobileclient_identity_pool",
                                                    allow_unauthenticated_identities=True,
                                                    # TODO:: Fix Identity Providers
                                                    # cognito_identity_providers=[
                                                    #     {"client_id" : user_pool_client.user_pool_client_id,
                                                    #      "provider_name" : user_pool.user_pool_provider_name,
                                                    #      "provider_type": "Google"}]
                                                    )

        identity_pool_auth_role_condition = {
            "StringEquals": {
                "cognito-identity.amazonaws.com:aud": identity_pool.ref
            },
            "ForAnyValue:StringLike": {
                "cognito-identity.amazonaws.com:amr": "authenticated"
            },
        }

        identity_pool_unauth_role_condition = {
            "StringEquals": {
                "cognito-identity.amazonaws.com:aud": identity_pool.ref
            },
            "ForAnyValue:StringLike": {
                "cognito-identity.amazonaws.com:amr": "unauthenticated"
            },
        }

        identity_pool_unauth_role = aws_iam.Role(self,
                                                 "CognitoDefaultUnauthenticatedRole",
                                                 assumed_by=aws_iam.FederatedPrincipal("cognito-identity.amazonaws.com",
                                                                                       identity_pool_unauth_role_condition,
                                                                                       "sts:AssumeRoleWithWebIdentity")
                                                 )
        identity_pool_unauth_role.add_to_policy(aws_iam.PolicyStatement(
                                                    effect=aws_iam.Effect.ALLOW,
                                                    actions=[
                                                        "mobileanalytics:PutEvents",
                                                        "cognito-sync:*",
                                                        "cognito-identity:*"
                                                    ],
                                                    resources=["*"]
                                                ))
        identity_pool_auth_role = aws_iam.Role(self,
                                               "CognitoDefaultAuthenticatedRole",
                                               assumed_by=aws_iam.FederatedPrincipal("cognito-identity.amazonaws.com",
                                                                                    identity_pool_auth_role_condition,
                                                                                     "sts:AssumeRoleWithWebIdentity")
                                               )
        identity_pool_auth_role.add_to_policy(aws_iam.PolicyStatement(
                                                    effect=aws_iam.Effect.ALLOW,
                                                    actions=[
                                                        "mobileanalytics:PutEvents",
                                                        "cognito-sync:*",
                                                        "cognito-identity:*"
                                                    ],
                                                    resources=["*"]
                                                ))

        identity_pool_role_attach = aws_cognito.CfnIdentityPoolRoleAttachment(self,
                                                                              "IdentityPoolRoleAttach",
                                                                              identity_pool_id=identity_pool.ref,
                                                                              roles={
                                                                                  "unauthenticated": identity_pool_unauth_role.role_arn,
                                                                                  "authenticated": identity_pool_auth_role.role_arn
                                                                              })

        string_parameter(self, "userpool_id", user_pool.user_pool_id)
        string_parameter(self, "pool_id_dev_auth", identity_pool.ref)

        circleci_execution_role.add_to_policy(aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                                                      actions=[
                                                                          "cognito-identity:*"],
                                                                      resources=["*"]
                                                                      ))

