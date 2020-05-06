from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class IotStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        identity_pool = cognito.CfnIdentityPool(
            self, "pinpoint_integ_test_android", allow_unauthenticated_identities=True
        )

        unauthenticated_role = iam.Role(
            self,
            "CognitoDefaultUnauthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                {
                    "StringEquals": {"cognito-identity.amazonaws.com:aud": identity_pool.ref},
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "unauthenticated"
                    },
                },
                "sts:AssumeRoleWithWebIdentity",
            ),
        )
        unauthenticated_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cognito-sync:*",
                    "iot:Connect",
                    "iot:Publish",
                    "iot:Subscribe",
                    "iot:Receive",
                    "iot:GetThingShadow",
                    "iot:DescribeEndpoint",
                    "iot:CreateKeysAndCertificate",
                    "iot:CreatePolicy",
                    "iot:AttachPolicy",
                ],
                resources=["*"],
            )
        )
        cognito.CfnIdentityPoolRoleAttachment(
            self,
            "DefaultValid",
            identity_pool_id=identity_pool.ref,
            roles={"unauthenticated": unauthenticated_role.role_arn},
        )

        self._parameters_to_save = {"identity_pool_id": identity_pool.ref}
        self.save_parameters_in_parameter_store(platform=Platform.ANDROID)

        stack_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, actions=["cognito-identity:*", "iot:*"], resources=["*"]
        )

        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)
