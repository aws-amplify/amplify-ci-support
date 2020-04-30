from aws_cdk import aws_iam, aws_pinpoint, core

from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack
from common.platforms import Platform


class PinpointStack(RegionAwareStack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 common_stack: CommonStack,
                 **kwargs) -> None:
        super().__init__(scope,
                         id,
                         **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        app = aws_pinpoint.CfnApp(self,
                                  "integ_test_app",
                                  name="integ_test_app")

        self._parameters_to_save = {"pinpointAppId": app.ref}
        self.save_parameters_in_parameter_store(platform=Platform.IOS)

        stack_policy = aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                               actions=[
                                                   "mobileanalytics:putEvents",
                                                   "mobiletargeting:PutEvents",
                                                   "mobiletargeting:UpdateEndpoint"
                                               ],
                                               resources=["*"])

        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)
