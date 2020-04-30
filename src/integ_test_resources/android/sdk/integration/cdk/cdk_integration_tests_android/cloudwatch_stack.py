from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import core

from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack


class CloudwatchStack(RegionAwareStack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 common_stack: CommonStack,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        log_group = logs.LogGroup(self, 'android-integ-test-log-group',
                                  log_group_name='com/amazonaws/tests')

        common_stack.add_to_common_role_policies(self)
