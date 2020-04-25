#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_android.pinpoint_stack import PinpointStack
from cdk_integration_tests_android.textract_stack import TextractStack
from cdk_integration_tests_android.apigateway_stack import ApiGatewayStack

app = core.App()

ApiGatewayStack(app, 'cdk-integration-tests-android-apigateway')
PinpointStack(app, 'cdk-integration-tests-android-pinpoint')
TextractStack(app, 'cdk-integration-tests-android-textract')

app.synth()
