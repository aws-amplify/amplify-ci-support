#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_ios.cdk_integration_tests_ios_stack import CdkIntegrationTestsIosStack


app = core.App()
CdkIntegrationTestsIosStack(app, "cdk-integration-tests-ios")

app.synth()
