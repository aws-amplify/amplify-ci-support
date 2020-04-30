#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_android.apigateway_stack import ApiGatewayStack
from cdk_integration_tests_android.cloudwatch_stack import CloudwatchStack
from cdk_integration_tests_android.core_stack import CoreStack
from cdk_integration_tests_android.iot_stack import IotStack
from cdk_integration_tests_android.kinesis_stack import KinesisStack
from cdk_integration_tests_android.pinpoint_stack import PinpointStack
from cdk_integration_tests_android.s3_stack import S3Stack

from common.common_stack import CommonStack
from common.main_stack import MainStack
from common.stack_utils import add_stack_dependency_on_common_stack
from common.platforms import Platform


app = core.App()

# Creates an execution role that can be used to run tests against the created resources
common_stack = CommonStack(app,
                           "common",
                           platform=Platform.ANDROID)

# The Main Stack is used to deploy all the resources that the tests will need.
# Users can also choose to only deploy the resources for the test suite they are interested in.
main_stack = MainStack(app, 'main')
main_stack.add_dependency(common_stack)

apigateway_stack = ApiGatewayStack(app,
                                   'apigateway',
                                   common_stack)

cloudwatch_stack = CloudwatchStack(app,
                                   'cloudwatch',
                                   common_stack)

core_stack = CoreStack(app,
                       'core',
                       common_stack)

iot_stack = IotStack(app,
                     'iot',
                     common_stack)

kinesis_stack = KinesisStack(app,
                             'kinesis',
                             common_stack)

pinpoint_stack = PinpointStack(app,
                               'pinpoint',
                               common_stack)

s3_stack = S3Stack(app,
                   's3',
                   common_stack)

stacks_in_app = [
    apigateway_stack,
    cloudwatch_stack,
    core_stack,
    iot_stack,
    kinesis_stack,
    pinpoint_stack,
    s3_stack
]

add_stack_dependency_on_common_stack(stacks_in_app=stacks_in_app,
                                     common_stack=common_stack)
main_stack.add_dependencies_with_region_filter(stacks_to_add=stacks_in_app)


app.synth()
