
from aws_cdk import aws_s3, core

class S3Stack(core.Stack):
    
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_name = "aws-sdk-ios-release-prod"

        self.bucket = aws_s3.Bucket(
            self, 
            "release_artifacts_ios_v2_sdk_release_bucket",
            bucket_name = bucket_name,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL
            )