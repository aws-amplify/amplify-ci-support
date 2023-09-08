from aws_cdk import aws_iam as iam
from constructs import Construct
from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack


class KmsStack(RegionAwareStack):
    def __init__(self, scope: Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        all_resources_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["kms:CreateKey"],
            resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

        alias_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["kms:CreateAlias"],
            resources=[f"arn:aws:kms:{self.region}:{self.account}:alias*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=alias_policy)

        key_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "kms:CancelKeyDeletion",
                "kms:CreateAlias",
                "kms:Decrypt",
                "kms:DescribeKey",
                "kms:DisableKeyRotation",
                "kms:Encrypt",
                "kms:ScheduleKeyDeletion",
            ],
            resources=[f"arn:aws:kms:{self.region}:{self.account}:key*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=key_policy)
