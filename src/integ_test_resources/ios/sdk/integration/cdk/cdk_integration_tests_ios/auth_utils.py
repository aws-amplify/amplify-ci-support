from aws_cdk import(
    aws_cognito,
    aws_iam,
    core
)

def construct_identity_pool(scope: core.Construct, **kwargs) -> (aws_cognito.CfnIdentityPool,
                                                                 aws_iam.Role,
                                                                 aws_iam.Role):

    cognito_identity_providers = kwargs.get("cognito_identity_providers", [])
    supported_login_providers = kwargs.get("supported_login_providers", {})
    identity_pool_unauth_role_policy = kwargs.get("identity_pool_unauth_role_policy",
                                                  aws_iam.PolicyStatement(
                                                      effect=aws_iam.Effect.ALLOW,
                                                      actions=[
                                                          "mobileanalytics:PutEvents",
                                                          "cognito-sync:*",
                                                          "cognito-idenity:*"
                                                      ],
                                                      resources=["*"]
                                                  ))
    identity_pool_auth_role_policy = kwargs.get("identity_pool_auth_role_policy",
                                                  aws_iam.PolicyStatement(
                                                      effect=aws_iam.Effect.ALLOW,
                                                      actions=[
                                                          "mobileanalytics:PutEvents",
                                                          "cognito-sync:*",
                                                          "cognito-idenity:*"
                                                      ],
                                                      resources=["*"]
                                                  ))

    identity_pool = aws_cognito.CfnIdentityPool(scope,
                                                "default_identity_pool",
                                                allow_unauthenticated_identities=True,
                                                # TODO:: Fix Identity Providers
                                                ## https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cognito.CfnIdentityPool.CognitoIdentityProviderProperty.html
                                                ## This API seems to be deprecated
                                                cognito_identity_providers=cognito_identity_providers,
                                                supported_login_providers = supported_login_providers
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

    identity_pool_unauth_role = aws_iam.Role(scope,
                                             "cognito_default_unauth_role",
                                             assumed_by=aws_iam.FederatedPrincipal("cognito-identity.amazonaws.com",
                                                                                   identity_pool_unauth_role_condition,
                                                                                   "sts:AssumeRoleWithWebIdentity")
                                             )
    identity_pool_unauth_role.add_to_policy(identity_pool_unauth_role_policy)
    identity_pool_auth_role = aws_iam.Role(scope,
                                           "cognito_default_auth_role",
                                           assumed_by=aws_iam.FederatedPrincipal("cognito-identity.amazonaws.com",
                                                                                 identity_pool_auth_role_condition,
                                                                                 "sts:AssumeRoleWithWebIdentity")
                                           )
    identity_pool_auth_role.add_to_policy(identity_pool_auth_role_policy)

    identity_pool_role_attach = aws_cognito.CfnIdentityPoolRoleAttachment(scope,
                                                                          "identity_pool_role_attach",
                                                                          identity_pool_id=identity_pool.ref,
                                                                          roles={
                                                                              "unauthenticated": identity_pool_unauth_role.role_arn,
                                                                              "authenticated": identity_pool_auth_role.role_arn
                                                                          })
    return (identity_pool,
            identity_pool_auth_role,
            identity_pool_unauth_role)
