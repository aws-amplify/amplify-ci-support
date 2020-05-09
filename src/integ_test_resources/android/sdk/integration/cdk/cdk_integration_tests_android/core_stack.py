from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class CoreStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        identity_pools = [self.identity_pool(i) for i in range(2)]

        self._supported_in_region = self.is_service_supported_in_region("cognito-identity")

        # Create an SSM parameter for the identity pool IDs
        self._parameters_to_save = {
            "identity_pool_id": identity_pools[0].ref,
            "other_identity_pool_id": identity_pools[1].ref,
        }
        self.save_parameters_in_parameter_store(platform=Platform.ANDROID)

        stack_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, actions=["cognito-identity:*"], resources=["*"]
        )

        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)

    def identity_pool(self, id) -> None:
        # Create the Cognito identity pool
        identity_pool = cognito.CfnIdentityPool(
            self,
            f"identityPool{id}",
            identity_pool_name="testIdentityPool",
            allow_unauthenticated_identities=True,
        )

        # Create the authenticated and authenticated roles
        unauth_role = iam.Role(
            self, f"unauthRole{id}", assumed_by=self.principal_for(identity_pool, "unauthenticated")
        )
        auth_role = iam.Role(
            self, f"authRole{id}", assumed_by=self.principal_for(identity_pool, "authenticated")
        )

        # Attach the two roles
        cognito.CfnIdentityPoolRoleAttachment(
            self,
            f"identityPoolRoles{id}",
            identity_pool_id=identity_pool.ref,
            roles={"authenticated": auth_role.role_arn, "unauthenticated": unauth_role.role_arn},
        )

        return identity_pool

    def principal_for(
        self, identity_pool: cognito.CfnIdentityPool, state: str
    ) -> iam.FederatedPrincipal:
        return iam.FederatedPrincipal(
            federated="cognito-identity.amazonaws.com",
            assume_role_action="sts:AssumeRoleWithWebIdentity",
            conditions={
                "StringEquals": {"cognito-identity.amazonaws.com:aud": identity_pool.ref},
                "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": state},
            },
        )
