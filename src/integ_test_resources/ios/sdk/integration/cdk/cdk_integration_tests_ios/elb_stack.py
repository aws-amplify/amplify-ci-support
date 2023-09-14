from aws_cdk import aws_iam as iam
from constructs import Construct
from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack


class ElbStack(RegionAwareStack):
    def __init__(self, scope: Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        all_resources_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "elasticloadbalancing:DescribeAccountLimits",
                "elasticloadbalancing:DescribeLoadBalancers",
            ],
            resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

        specified_resources_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["elasticloadbalancing:ConfigureHealthCheck"],
            resources=[f"arn:aws:elasticloadbalancing:{self.region}:{self.account}:loadbalancer/*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=specified_resources_policy)
