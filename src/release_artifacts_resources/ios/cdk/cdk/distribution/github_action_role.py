from aws_cdk import core, aws_iam, aws_s3

class GithubActionRole(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str, bucket: aws_s3.Bucket):
        super().__init__(scope, construct_id)

        self.provider = aws_iam.OpenIdConnectProvider(self, "GithubAction",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"]
        )

        self.principal = aws_iam.OpenIdConnectPrincipal(self.provider,
            conditions={
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    "token.actions.githubusercontent.com:sub": "repo:aws-amplify/aws-sdk-ios:ref:refs/heads/release"
                }
            }
        )

        aws_iam.Role(self, "Role",
            assumed_by=self.principal,
            inline_policies={
                "writeS3ReleaseBucket": aws_iam.PolicyDocument(
                    statements=[aws_iam.PolicyStatement(
                        actions=[
                            "s3:PutObject"
                        ],
                        resources=[f"{bucket.bucket_arn}/*"]
                    )]
                )
            }
        )


