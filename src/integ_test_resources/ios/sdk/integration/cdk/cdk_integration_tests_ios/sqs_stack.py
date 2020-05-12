from aws_cdk import aws_iam, aws_sqs, core

from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack


class SqsStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        # Test simply asserts the existence of a queue
        aws_sqs.Queue(self, "integ_test_sqs_queue")

        queue_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["sqs:GetQueueAttributes"],
            resources=[f"arn:aws:sqs:{self.region}:{self.account}:*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=queue_policy)

        all_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["sqs:ListQueues"], resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)
