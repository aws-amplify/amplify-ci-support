from datetime import datetime

from aws_cdk import aws_cloudfront, core
from aws_cdk import aws_cloudfront_origins
from cdk.s3_stack import S3Stack

class CloudFrontStack(core.Stack):
    
    def __init__(
        self,
        scope: core.Construct, 
        construct_id: str,
        s3_Stack: S3Stack,
        **kwargs
        ) -> None:
        
        super().__init__(scope, construct_id, **kwargs)

        cloudfront = aws_cloudfront.Distribution(
            self,
            "release_artifacts_cloudfront",
             default_behavior=aws_cloudfront.BehaviorOptions(origin=aws_cloudfront_origins.S3Origin(s3_Stack.bucket))
        )
        
        # We do not want someone to accidently delete the Cloudfront resources. This is created as RETAIN so that
        # tearing down cloudformation doesnot remove the cloudfront distribution.
        cloudfront.apply_removal_policy(core.RemovalPolicy.RETAIN)
