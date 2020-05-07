from aws_cdk import aws_iam, core

from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack


class AutoScalingStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        describe_account_limits_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["autoscaling:DescribeAccountLimits"],
            resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=describe_account_limits_policy)

        attach_instances_arn = "arn:aws:autoscaling:{}:{}:autoScalingGroup:*:autoScalingGroupName/*".format(  # noqa: E501
            self.region, self.account
        )
        attach_instances_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["autoscaling:AttachInstances"],
            resources=[attach_instances_arn],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=attach_instances_policy)
