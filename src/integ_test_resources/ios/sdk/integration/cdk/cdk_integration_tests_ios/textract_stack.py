from aws_cdk import aws_iam as iam
from constructs import Construct
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class TextractStack(RegionAwareStack):
    def __init__(self, scope: Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        all_resources_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, actions=["textract:AnalyzeDocument"], resources=["*"]
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

        self.save_parameters_in_parameter_store(Platform.IOS)
