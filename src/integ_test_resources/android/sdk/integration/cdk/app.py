#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_android.apigateway_stack import ApiGatewayStack
from cdk_integration_tests_android.cloudwatch_stack import CloudwatchStack
from cdk_integration_tests_android.core_stack import CoreStack
from cdk_integration_tests_android.iot_stack import IotStack
from cdk_integration_tests_android.kinesis_stack import KinesisStack
from cdk_integration_tests_android.main_stack import MainStack
from cdk_integration_tests_android.pinpoint_stack import PinpointStack
from cdk_integration_tests_android.s3_stack import S3Stack

from common.common_stack import CommonStack


app = core.App()

# Creates an execution role that can be used to run tests against the created resources
common_stack = CommonStack(app, "common")

apigateway_stack = ApiGatewayStack(app, 'apigateway', common_stack.circleci_execution_role)
apigateway_stack.add_dependency(common_stack)
cloudwatch_stack = CloudwatchStack(app, 'cloudwatch', common_stack.circleci_execution_role)
cloudwatch_stack.add_dependency(common_stack)
core_stack = CoreStack(app, 'core', common_stack.circleci_execution_role)
core_stack.add_dependency(common_stack)
iot_stack = IotStack(app, 'iot', common_stack.circleci_execution_role)
iot_stack.add_dependency(common_stack)
kinesis_stack = KinesisStack(app, 'kinesis', common_stack.circleci_execution_role)
kinesis_stack.add_dependency(common_stack)
pinpoint_stack = PinpointStack(app, 'pinpoint', common_stack.circleci_execution_role)
pinpoint_stack.add_dependency(common_stack)
s3_stack = S3Stack(app, 's3', common_stack.circleci_execution_role)
s3_stack.add_dependency(common_stack)

# The Main Stack is used to deploy all the resources that the tests will need.
# Users can also choose to only deploy the resources for the test suite they are interested in.
main_stack = MainStack(app, 'main')
main_stack.add_dependency(apigateway_stack)
main_stack.add_dependency(cloudwatch_stack)
main_stack.add_dependency(common_stack)
main_stack.add_dependency(core_stack)
main_stack.add_dependency(iot_stack)
main_stack.add_dependency(kinesis_stack)
main_stack.add_dependency(pinpoint_stack)

app.synth()
