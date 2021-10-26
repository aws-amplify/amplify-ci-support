from aws_cdk import aws_s3, core

class S3Construct(core.Construct):
    def __init__(
        self, 
        scope: core.Construct, 
        construct_id: str, 
        bucketPrefix: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        logging_bucket_name = bucketPrefix + "amplify-ios-integ-access-logging"
        access_log_bucket = aws_s3.Bucket(
            self,
            "amplify-ios-integ-access-logging",
            bucket_name=logging_bucket_name,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        self.bucket_name = bucketPrefix + "amplify-ios-integ"
        self.bucket = aws_s3.Bucket(
            self,
            "amplify-ios-integ-configuration_bucket",
            bucket_name=self.bucket_name,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=core.RemovalPolicy.DESTROY,
            server_access_logs_bucket=access_log_bucket,
            versioned=True,
            encryption=aws_s3.BucketEncryption.S3_MANAGED,
        )
