from aws_cdk import aws_pinpoint as pinpoint
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import core

from common.parameters import string_parameter


class PinpointStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 circleci_execution_role: iam.Role,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        app = pinpoint.CfnApp(self, 'android-integ-test',
                                  name='android-integ-test')

        identity_pool = cognito.CfnIdentityPool(
            self,
            'pinpoint_integ_test_android',
            allow_unauthenticated_identities=True)

        unauthenticated_role = iam.Role(
            self,
            'CognitoDefaultUnauthenticatedRole',
            assumed_by=iam.FederatedPrincipal(
                'cognito-identity.amazonaws.com', {
                    'StringEquals': {'cognito-identity.amazonaws.com:aud':
                                     identity_pool.ref},
                    'ForAnyValue:StringLike': {
                        'cognito-identity.amazonaws.com:amr':
                        'unauthenticated'},
                }, 'sts:AssumeRoleWithWebIdentity'))
        unauthenticated_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'cognito-sync:*',
                'mobiletargeting:PutEvents'
            ],
            resources=['*']
        ))
        cognito.CfnIdentityPoolRoleAttachment(
            self,
            'DefaultValid',
            identity_pool_id=identity_pool.ref,
            roles={
                'unauthenticated': unauthenticated_role.role_arn
            }
        )

        string_parameter(self, 'identity_pool_id', identity_pool.ref)
        string_parameter(self, 'AppId', app.ref)
        string_parameter(self, 'Region', core.Aws.REGION)

        circleci_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["mobileanalytics:PutEvents",
                         "mobiletargeting:PutEvents",
                         "mobiletargeting:UpdateEndpoint"], resources=["*"]))
