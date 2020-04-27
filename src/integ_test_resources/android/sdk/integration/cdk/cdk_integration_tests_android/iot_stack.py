from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import core

import sys
import os
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '../../../../..'))
from common.parameters import string_parameter


class IotStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 circleci_execution_role: iam.Role,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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
                'iot:Connect',
                'iot:Publish',
                'iot:Subscribe',
                'iot:Receive',
                'iot:GetThingShadow',
                'iot:DescribeEndpoint',
                'iot:CreateKeysAndCertificate',
                'iot:CreatePolicy',
                'iot:AttachPolicy'
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

        circleci_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["cognito-identity:*", "iot:*"], resources=["*"]))
