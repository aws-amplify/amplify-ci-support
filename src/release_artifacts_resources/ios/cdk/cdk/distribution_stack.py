from aws_cdk import core as cdk
from cdk.distribution.cloudfront_construct import CloudFrontConstruct
from cdk.distribution.s3_construct import S3Construct
from cdk.distribution.github_action_role import GithubActionRole


class DistributionStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.s3 = S3Construct(self, "distribution_s3_construct")
        self.cloudfront = CloudFrontConstruct(self, "distribution_cloudfront_construct", self.s3)
        self.github_action_role = GithubActionRole(self, "github_action_role", bucket=self.s3.bucket)
