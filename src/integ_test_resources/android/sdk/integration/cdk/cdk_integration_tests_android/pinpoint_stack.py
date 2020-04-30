from aws_cdk import aws_pinpoint as pinpoint
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import core

from common.region_aware_stack import RegionAwareStack
from common.platforms import Platform
from common.common_stack import CommonStack

class PinpointStack(RegionAwareStack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 common_stack: CommonStack,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

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

        self._parameters_to_save = {
            "identity_pool_id": identity_pool.ref,
            "AppId": app.ref,
            "Region": core.Aws.REGION
        }
        self.save_parameters_in_parameter_store(platform=Platform.ANDROID)

        stack_policy = iam.PolicyStatement(effect=iam.Effect.ALLOW,
                                           actions=[
                                               "mobileanalytics:PutEvents",
                                               "mobiletargeting:PutEvents",
                                               "mobiletargeting:UpdateEndpoint"
                                           ],
                                           resources=["*"])

        common_stack.add_to_common_role_policies(self,
                                                 policy_to_add=stack_policy)
