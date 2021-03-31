#!/usr/bin/env python3

from aws_cdk import core as cdk
from cdk.s3_stack import S3Stack
from cdk.cloudfront_stack import CloudFrontStack

from aws_cdk import core

from cdk.cdk_stack import CdkStack

def raiseOperationValueError():
    raise ValueError(
        "Provide operation with value either 'CREDENTIAL_ROTATION' or 'RELEASE_HOST' in 'context' parameter, as in: cdk deploy app -c operation=CREDENTIAL_ROTATION"  # noqa: E501
    )

app = core.App()

operation = app.node.try_get_context("operation")
if operation is None:
    raiseOperationValueError()

main = CdkStack(app, "MainStack")

if operation == 'RELEASE_HOST':
    
    s3_stack = S3Stack(app, "S3Stack")
    cloudfront_stack = CloudFrontStack(app, "CloudfrontStack", s3_stack)
    cloudfront_stack.add_dependency(s3_stack)

    main.add_dependency(s3_stack)
    main.add_dependency(cloudfront_stack)
# elif operation == 'CREDENTIAL_ROTATION':
#     # iam_stack = IAMStack(app, "IAMStack", bucket_arn="sd", cloudfront_arn="sd")
#     # lambda_stack = LambdaStack(app, "LambdaStack", iam_stack=iam_stack)
else:
    raiseOperationValueError()

app.synth()
