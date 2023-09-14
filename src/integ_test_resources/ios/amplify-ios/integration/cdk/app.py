#!/usr/bin/env python3

from aws_cdk import App
from cdk_integration_tests_ios.integration_test_resources_stack import IntegrationTestResourcesStack
app = App()

BUCKET_PREFIX = app.node.try_get_context("bucket_prefix")
if BUCKET_PREFIX is None:
    raise ValueError(
        "Provide unique bucket prefix to prefix the S3 bucket , as in: cdk deploy app -c bucket_prefix=iosinteg"  # noqa: E501
    )
IntegrationTestResourcesStack(
    app,
    "IntegrationTestResourcesStack",
    bucketPrefix=BUCKET_PREFIX
    )

app.synth()
