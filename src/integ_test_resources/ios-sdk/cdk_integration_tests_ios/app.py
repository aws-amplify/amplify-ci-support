#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_ios.common_stack import CommonStack
from cdk_integration_tests_ios.apigateway_stack import ApigatewayStack
from cdk_integration_tests_ios.mobileclient_stack import MobileclientStack
from cdk_integration_tests_ios.lambda_stack import LambdaStack


app = core.App()

common_stack = CommonStack(app, "common-stack")


lambda_stack = LambdaStack(app,
                           "lambda",
                           common_stack.circleci_execution_role)
lambda_stack.add_dependency(common_stack)

apigateway_stack = ApigatewayStack(app,
                                   "apigateway",
                                   lambda_stack.lambda_echo_function,
                                   common_stack.circleci_execution_role)

apigateway_stack.add_dependency(common_stack)

mobileclient_stack = MobileclientStack(app,
                                       "mobileclient",
                                       common_stack.circleci_execution_role)
mobileclient_stack.add_dependency(common_stack)

app.synth()


