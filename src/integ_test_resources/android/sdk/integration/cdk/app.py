#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_android.apigateway_stack import ApiGatewayStack
from cdk_integration_tests_android.core_stack import CoreStack
from cdk_integration_tests_android.pinpoint_stack import PinpointStack
from cdk_integration_tests_android.textract_stack import TextractStack


app = core.App()

ApiGatewayStack(app, 'apigateway')
CoreStack(app, 'core')
PinpointStack(app, 'pinpoint')
TextractStack(app, 'textract')

app.synth()
