#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_android.apigateway_stack import ApiGatewayStack
from cdk_integration_tests_android.core_stack import CoreStack
from cdk_integration_tests_android.pinpoint_stack import PinpointStack
from cdk_integration_tests_android.s3_stack import S3Stack


app = core.App()

ApiGatewayStack(app, 'apigateway')
CoreStack(app, 'core')
PinpointStack(app, 'pinpoint')
S3Stack(app, 's3')

app.synth()
