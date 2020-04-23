from aws_cdk import(
    core,
    aws_pinpoint,
    aws_cognito,
    aws_iam,
    aws_s3,
    aws_s3_deployment
)

class PinpointStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        app = aws_pinpoint.CfnApp(self, 'android-integ-test', name='android-integ-test')

        identity_pool = aws_cognito.CfnIdentityPool(self, 'pinpoint_integ_test_android', allow_unauthenticated_identities=True)

        unauthenticated_role = aws_iam.Role(self, 'CognitoDefaultUnauthenticatedRole',
            assumed_by = aws_iam.FederatedPrincipal('cognito-identity.amazonaws.com', {
                "StringEquals": { "cognito-identity.amazonaws.com:aud": identity_pool.ref },
                "ForAnyValue:StringLike": { "cognito-identity.amazonaws.com:amr": "unauthenticated" },
            }, "sts:AssumeRoleWithWebIdentity"))
        unauthenticated_role.add_to_policy(aws_iam.PolicyStatement(
            effect = aws_iam.Effect.ALLOW,
            actions = [
                "mobileanalytics:PutEvents",
                "cognito-sync:*",
                "mobiletargeting:UpdateEndpoint",
                "mobiletargeting:PutEvents"
            ],
            resources = ["*"]
        ))
        authenticated_role = aws_iam.Role(self, 'CognitoDefaultAuthenticatedRole', 
            assumed_by = aws_iam.FederatedPrincipal('cognito-identity.amazonaws.com', {
                "StringEquals": { "cognito-identity.amazonaws.com:aud": identity_pool.ref },
                "ForAnyValue:StringLike": { "cognito-identity.amazonaws.com:amr": "authenticated" },
            }, "sts:AssumeRoleWithWebIdentity"))
        authenticated_role.add_to_policy(aws_iam.PolicyStatement(
            effect = aws_iam.Effect.ALLOW,
            actions = [
                "mobileanalytics:PutEvents",
                "cognito-sync:*",
                "cognito-identity:*"
            ],
            resources = ["*"]
        ))
        default_policy = aws_cognito.CfnIdentityPoolRoleAttachment(self, 'DefaultValid',
            identity_pool_id = identity_pool.ref,
            roles = {
                'unauthenticated': unauthenticated_role.role_arn,
                'authenticated': authenticated_role.role_arn
            }
        )

        core.CfnOutput(self, "identity_pool_id", value = identity_pool.ref);
        core.CfnOutput(self, "app_id", value = app.ref);