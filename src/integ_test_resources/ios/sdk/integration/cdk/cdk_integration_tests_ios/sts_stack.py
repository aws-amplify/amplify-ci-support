from aws_cdk import aws_iam, core
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class StsStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        # Create a role with no permissions to test the SDKs assumeRole API
        test_role = aws_iam.Role(
            self, "sts_test_role", assumed_by=common_stack.circleci_execution_role
        )
        self._parameters_to_save = {"testRoleArn": test_role.role_arn}
        self.save_parameters_in_parameter_store(platform=Platform.IOS)
