#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_ios.apigateway_stack import ApigatewayStack
from cdk_integration_tests_ios.autoscaling_stack import AutoScalingStack
from cdk_integration_tests_ios.cloudwatch_stack import CloudWatchStack
from cdk_integration_tests_ios.cognito_idp_stack import CognitoIdpStack
from cdk_integration_tests_ios.core_stack import CoreStack
from cdk_integration_tests_ios.lambda_stack import LambdaStack
from cdk_integration_tests_ios.mobileclient_stack import MobileClientStack
from cdk_integration_tests_ios.pinpoint_stack import PinpointStack
from cdk_integration_tests_ios.sns_stack import SnsStack
from cdk_integration_tests_ios.sts_stack import StsStack
from common.common_stack import CommonStack
from common.main_stack import MainStack
from common.platforms import Platform
from common.stack_utils import add_stack_dependency_on_common_stack

app = core.App()

common_stack = CommonStack(app, "common", platform=Platform.IOS)
main_stack = MainStack(app, "main")
main_stack.add_dependency(common_stack)

core_stack = CoreStack(app, "core", common_stack)

lambda_stack = LambdaStack(app, "lambda", common_stack)

apigateway_stack = ApigatewayStack(
    app, "apigateway", lambda_stack.lambda_echo_function, common_stack
)

autoscaling_stack = AutoScalingStack(app, "autoscaling", common_stack)
cloudwatch_stack = CloudWatchStack(app, "cloudwatch", common_stack)
cognito_idp_stack = CognitoIdpStack(app, "cognito-idp", common_stack)
mobileclient_stack = MobileClientStack(app, "mobileclient", common_stack)
pinpoint_stack = PinpointStack(app, "pinpoint", common_stack)
sns_stack = SnsStack(app, "sns", common_stack)
sts_stack = StsStack(app, "sts", common_stack)

stacks_in_app = [
    core_stack,
    apigateway_stack,
    autoscaling_stack,
    cloudwatch_stack,
    cognito_idp_stack,
    lambda_stack,
    mobileclient_stack,
    pinpoint_stack,
    sns_stack,
    sts_stack,
]

add_stack_dependency_on_common_stack(stacks_in_app=stacks_in_app, common_stack=common_stack)
main_stack.add_dependencies_with_region_filter(stacks_to_add=stacks_in_app)

app.synth()
