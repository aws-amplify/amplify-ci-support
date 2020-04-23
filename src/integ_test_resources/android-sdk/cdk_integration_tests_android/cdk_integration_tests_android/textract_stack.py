from aws_cdk import(
    core,
    aws_s3
)

class TextractStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        bucket = aws_s3.Bucket(self, 'aws-android-sdk-textract')

        core.CfnOutput(self, "s3_bucket_name", value = bucket.bucket_arn);