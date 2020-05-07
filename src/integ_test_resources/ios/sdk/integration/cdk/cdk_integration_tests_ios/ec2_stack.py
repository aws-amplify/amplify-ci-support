from aws_cdk import aws_iam, core

from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack


class Ec2Stack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        all_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["ec2:DescribeImages", "ec2:DescribeInstances"],
            resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)
