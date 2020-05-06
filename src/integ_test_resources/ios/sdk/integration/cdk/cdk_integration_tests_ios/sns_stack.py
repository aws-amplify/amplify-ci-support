from aws_cdk import aws_iam, aws_sns, core

from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack


class SnsStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        all_resources_arn = self.format_arn(
            resource="*",
            service=id
        )

        stack_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["sns:ListTopics"],
            resources=[all_resources_arn],
        )

        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)
