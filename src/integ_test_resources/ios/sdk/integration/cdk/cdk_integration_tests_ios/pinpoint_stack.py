from aws_cdk import aws_iam, aws_pinpoint, core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class PinpointStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        pinpoint_app = aws_pinpoint.CfnApp(
            self, "integ_test_pinpoint_app", name="integ_test_pinpoint_app"
        )
        self._parameters_to_save["app_id"] = pinpoint_app.ref

        legacy_mobileanalytics_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["mobileanalytics:putEvents"],
            resources=[self.format_arn(resource="*", service="mobileanalytics")],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=legacy_mobileanalytics_policy)

        app_arn = f"arn:aws:mobiletargeting:{self.region}:{self.account}:apps/*"
        app_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["mobiletargeting:PutEvents", "mobiletargeting:UpdateEndpoint"],
            resources=[app_arn],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=app_policy)

        self.save_parameters_in_parameter_store(platform=Platform.IOS)
