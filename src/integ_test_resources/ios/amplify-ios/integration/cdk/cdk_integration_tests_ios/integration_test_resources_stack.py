from aws_cdk import core as cdk
from cdk_integration_tests_ios.integration_test_resources.s3_construct import S3Construct
from cdk_integration_tests_ios.integration_test_resources.iam_construct import IAMConstruct

class IntegrationTestResourcesStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        bucketPrefix: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_construct = S3Construct(
            self, 
            "integration_test_resources_s3",
            bucketPrefix=bucketPrefix
        )

        IAMConstruct(
            self, "integration_test_resources_iam", 
            bucket_arn=s3_construct.bucket.bucket_arn
        )


            