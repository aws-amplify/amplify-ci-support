#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_ios.apigateway_stack import ApigatewayStack
from cdk_integration_tests_ios.core_stack import CoreStack
from cdk_integration_tests_ios.lambda_stack import LambdaStack
from cdk_integration_tests_ios.main_stack import MainStack
from cdk_integration_tests_ios.mobileclient_stack import MobileClientStack
from cdk_integration_tests_ios.pinpoint_stack import PinpointStack
from common.common_stack import CommonStack
from common.platforms import Platform
from common.stack_utils import add_stack_dependency_on_common_stack

app = core.App()

common_stack = CommonStack(app,
                           "common",
                           platform=Platform.IOS)
main_stack = MainStack(app, "main")
main_stack.add_dependency(common_stack)

core_stack = CoreStack(app,
                       "core",
                       common_stack)

lambda_stack = LambdaStack(app,
                           "lambda",
                           common_stack)

apigateway_stack = ApigatewayStack(app,
                                   "apigateway",
                                   lambda_stack.lambda_echo_function,
                                   common_stack)

mobileclient_stack = MobileClientStack(app,
                                       "mobileclient",
                                       common_stack)

pinpoint_stack = PinpointStack(app,
                               "pinpoint",
                               common_stack)

stacks_in_app = [
    core_stack,
    lambda_stack,
    apigateway_stack,
    mobileclient_stack,
    pinpoint_stack
]

add_stack_dependency_on_common_stack(stacks_in_app=stacks_in_app,
                                     common_stack=common_stack)
main_stack.add_dependencies_with_region_filter(stacks_to_add=stacks_in_app)

app.synth()
