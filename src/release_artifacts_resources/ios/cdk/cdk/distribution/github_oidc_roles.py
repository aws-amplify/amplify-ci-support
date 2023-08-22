from aws_cdk import core, aws_iam, aws_s3, aws_cloudfront

# This construct is dedicated for Github workflows to retrieve AWS credential with OIDC
class GithubOIDCRoles(core.Construct):
    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        bucket: aws_s3.Bucket,
        cloudfront_distribution: aws_cloudfront.Distribution
    ):
        super().__init__(scope, construct_id)

        self.provider = aws_iam.OpenIdConnectProvider(self, "github_oidc",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"]
        )

        release_artifacts_principal = aws_iam.OpenIdConnectPrincipal(self.provider,
            conditions={
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    "token.actions.githubusercontent.com:sub": "repo:aws-amplify/aws-sdk-ios:environment:ReleaseArtifacts"
                }
            }
        )

        aws_iam.Role(self, "aws_sdk_ios_release_artifacts",
            assumed_by=release_artifacts_principal,
            inline_policies={
                "writeS3ReleaseBucket": aws_iam.PolicyDocument(
                    statements=[aws_iam.PolicyStatement(
                        actions=[
                            "s3:PutObject"
                        ],
                        resources=[f"{bucket.bucket_arn}/*"]
                    )]
                ),
                "invalidateCloudFrontDistribution": aws_iam.PolicyDocument(
                    statements=[aws_iam.PolicyStatement(
                        actions=["cloudfront:CreateInvalidation"],
                        resources=[f"arn:aws:cloudfront::{core.Stack.of(self).account}:distribution/{cloudfront_distribution.distribution_id}"]
                    )]
                )
            }
        )
