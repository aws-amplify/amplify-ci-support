from aws_cdk import aws_iam, core
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class StsStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        assumed_by_principal = common_stack.circleci_execution_role
        if common_stack.github_action_oidc is not None:
            assumed_by_principal = aws_iam.CompositePrincipal(
                common_stack.circleci_execution_role,
                common_stack.github_action_oidc.aws_sdk_ios_integration_test_role
            )

        # Create a role with no permissions to test the SDKs assumeRole API
        test_role = aws_iam.Role(
            self, "sts_test_role",
            assumed_by=assumed_by_principal
        )
        self._parameters_to_save = {"testRoleArn": test_role.role_arn}
        self.save_parameters_in_parameter_store(platform=Platform.IOS)
