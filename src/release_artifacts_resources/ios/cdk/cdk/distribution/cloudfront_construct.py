from aws_cdk import aws_cloudfront, aws_cloudfront_origins, core
from cdk.distribution.s3_construct import S3Construct


class CloudFrontConstruct(core.Construct):
    def __init__(
        self, scope: core.Construct, construct_id: str, s3_construct: S3Construct, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        self.distribution = aws_cloudfront.Distribution(
            self,
            "release_artifacts_cloudfront",
            default_behavior=aws_cloudfront.BehaviorOptions(
                origin=aws_cloudfront_origins.S3Origin(s3_construct.bucket),
                viewer_protocol_policy=aws_cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
            ),
        )

        # We do not want someone to accidentally delete the
        # CloudFront distribution, since that would break
        # publicly-available distribution mechanisms. Set
        # the removal policy to RETAIN so that deleting
        # the `cloudformation` stack does not remove the
        # CloudFront resource.
        self.distribution.apply_removal_policy(core.RemovalPolicy.RETAIN)
