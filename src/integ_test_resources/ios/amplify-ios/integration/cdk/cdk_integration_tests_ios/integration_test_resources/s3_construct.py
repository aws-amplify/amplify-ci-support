from constructs import Construct
from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3 as s3

class S3Construct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucketPrefix: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        logging_bucket_name = bucketPrefix + "amplify-ios-integ-access-logging"
        access_log_bucket = s3.Bucket(
            self,
            "amplify-ios-integ-access-logging",
            bucket_name=logging_bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
        )

        bucket_name = bucketPrefix + "amplify-ios-integ"
        self.bucket = s3.Bucket(
            self,
            "amplify-ios-integ-configuration_bucket",
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            server_access_logs_bucket=access_log_bucket,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )
