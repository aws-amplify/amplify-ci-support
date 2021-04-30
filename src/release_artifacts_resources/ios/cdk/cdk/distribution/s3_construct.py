from aws_cdk import aws_s3, core


class S3Construct(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        logging_bucket_name = "aws-sdk-ios-release-access-logging"
        access_log_bucket = aws_s3.Bucket(
            self,
            "release_artifacts_ios_v2_sdk_release_bucket_access_logging",
            bucket_name=logging_bucket_name,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=core.RemovalPolicy.RETAIN,
        )

        bucket_name = "aws-sdk-ios-release"

        self.bucket = aws_s3.Bucket(
            self,
            "release_artifacts_ios_v2_sdk_release_bucket",
            bucket_name=bucket_name,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=core.RemovalPolicy.RETAIN,
            server_access_logs_bucket=access_log_bucket,
            versioned=True,
            encryption=aws_s3.BucketEncryption.S3_MANAGED,
        )
