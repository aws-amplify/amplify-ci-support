#!/usr/bin/env python3
import json
import os

from aws_cdk import core

from cdk_integration_tests_ios.apigateway_stack import ApigatewayStack
from cdk_integration_tests_ios.common_stack import CommonStack
from cdk_integration_tests_ios.core_stack import CoreStack
from cdk_integration_tests_ios.lambda_stack import LambdaStack
from cdk_integration_tests_ios.main_stack import MainStack
from cdk_integration_tests_ios.mobileclient_stack import MobileClientStack
from cdk_integration_tests_ios.pinpoint_stack import PinpointStack
from secrets_manager import get_ios_integ_tests_secrets
from s3_stack import S3Stack
from cdk_stack_extension import CDKStackExtension

app = core.App()
ios_integ_tests_secrets = json.loads(get_ios_integ_tests_secrets())

stacks_in_app = []
common_stack = CommonStack(app, "common")
stacks_in_app.append(common_stack)

core_stack = CoreStack(app,
                       "core",
                       common_stack,
                       facebook_app_id=ios_integ_tests_secrets["IOS_FB_AWSCORETESTS_APP_ID"],
                       facebook_app_secret=ios_integ_tests_secrets["IOS_FB_AWSCORETESTS_APP_SECRET"])
stacks_in_app.append(core_stack)

lambda_stack = LambdaStack(app,
                           "lambda",
                           common_stack)
stacks_in_app.append(lambda_stack)

apigateway_stack = ApigatewayStack(app,
                                   "apigateway",
                                   lambda_stack.lambda_echo_function,
                                   common_stack)
stacks_in_app.append(apigateway_stack)

mobileclient_stack = MobileClientStack(app,
                                       "mobileclient",
                                       common_stack)
stacks_in_app.append(mobileclient_stack)

pinpoint_stack = PinpointStack(app,
                               "pinpoint",
                               common_stack)
stacks_in_app.append(pinpoint_stack)

s3_stack = S3Stack(app,
                   "s3",
                   common_stack)
stacks_in_app.append(s3_stack)

main_stack = MainStack(app, "main")

def add_dependency_on_common_stack(stacks_in_app):
    for stack in stacks_in_app:
        stack.add_dependency(common_stack)

def add_dependencies_for_main_stack(stacks_in_app,
                                    main_stack: CDKStackExtension):
    for stack in stacks_in_app:
        if stack._supported_in_region:
            main_stack.add_dependency(stack)

add_dependency_on_common_stack(stacks_in_app)
add_dependencies_for_main_stack(stacks_in_app,
                                main_stack=main_stack)
app.synth()
