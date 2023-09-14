from aws_cdk import aws_iam as iam
from constructs import Construct
from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack


class DynamoDbStack(RegionAwareStack):
    def __init__(self, scope: Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        all_resources_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, actions=["dynamodb:ListTables"], resources=["*"]
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

        table_resources_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:CreateTable",
                "dynamodb:DeleteTable",
                "dynamodb:DescribeTable",
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
                "dynamodb:UpdateTable",
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=table_resources_policy)
