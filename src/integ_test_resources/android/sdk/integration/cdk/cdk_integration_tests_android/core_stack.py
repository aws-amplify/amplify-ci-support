from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import core

from parameters import string_parameter


class CoreStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the Cognito identity pool
        identity_pool = cognito.CfnIdentityPool(
            self, 'identityPool',
            identity_pool_name='testIdentityPool',
            allow_unauthenticated_identities=True
        )

        # Create the authenticated and authenticated roles
        # TODO: The auth role will likely need additional permissions as there's
        # some coupling to the Kinesis tests.
        unauth_role = iam.Role(
            self, 'unauthRole',
            assumed_by=self.principal_for(identity_pool, 'unauthenticated')
         )
        auth_role = iam.Role(
            self, 'authRole',
            assumed_by=self.principal_for(identity_pool, 'authenticated')
         )

        # Attach the two roles
        cognito.CfnIdentityPoolRoleAttachment(
            self, 'identityPoolRoles',
            identity_pool_id=identity_pool.ref,
            roles={
                'authenticated': auth_role.role_arn,
                'unauthenticated': unauth_role.role_arn
            }
        )

        # Create an SSM parameter for the identity pool ID
        # endpoint, and the API key
        string_parameter(self, 'identity_pool_id', identity_pool.ref)

    def principal_for(
            self,
            identity_pool: cognito.CfnIdentityPool,
            state: str
    ) -> iam.FederatedPrincipal:
        return iam.FederatedPrincipal(
            federated='cognito-identity.amazonaws.com',
            assume_role_action='sts:AssumeRoleWithWebIdentity',
            conditions={
                'StringEquals': {
                    'cognito-identity.amazonaws.com:aud': identity_pool.ref
                 },
                'ForAnyValue:StringLike': {
                    'cognito-identity.amazonaws.com:amr': state
                }
            }
        )
