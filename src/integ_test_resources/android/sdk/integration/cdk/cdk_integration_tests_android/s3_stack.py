from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_s3 as s3
from aws_cdk import core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class S3Stack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        # Create policy for KMS key
        policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    actions=["kms:*"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                    principals=[iam.AccountPrincipal(core.Aws.ACCOUNT_ID)],
                )
            ]
        )

        # Create KMS key for S3 server-side encryption
        key = kms.Key(self, "s3SSETestkmsKey", policy=policy)

        # Create S3 bucket for SSE testing
        bucket = s3.Bucket(
            self, "s3TestBucket", encryption=s3.BucketEncryption.KMS, encryption_key=key
        )

        # Create SSM parameters for the KMS key id, KMS bucket name and region
        self._parameters_to_save = {
            "sse_kms_key_id": key.key_id,
            "bucket_with_sse_kms_enabled": bucket.bucket_name,
            "bucket_with_sse_kms_region": core.Aws.REGION,
        }
        self.save_parameters_in_parameter_store(platform=Platform.ANDROID)

        common_stack.add_to_common_role_policies(self)
