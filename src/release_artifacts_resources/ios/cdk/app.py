#!/usr/bin/env python3

from aws_cdk import core
from cdk.credential_rotation_stack import CredentialRotationStack
from cdk.distribution_stack import DistributionStack

app = core.App()

distribution_stack = DistributionStack(app, "DistributionStack")

bucket_arn = distribution_stack.s3.bucket.bucket_arn
bucket_name = distribution_stack.s3.bucket.bucket_name
cloudfront_distribution_id = distribution_stack.cloudfront.distribution.distribution_id
arn_components = core.ArnComponents(
    resource="distribution/" + cloudfront_distribution_id, service="cloudfront", region=""
)
cloudfront_arn = core.Arn.format(components=arn_components, stack=distribution_stack)

credential_rotation_stack = CredentialRotationStack(
    app,
    "CredentialRotationStack",
    bucket_name=bucket_name,
    bucket_arn=bucket_arn,
    cloudfront_distribution_id=cloudfront_distribution_id,
    cloudfront_arn=cloudfront_arn,
)

app.synth()
