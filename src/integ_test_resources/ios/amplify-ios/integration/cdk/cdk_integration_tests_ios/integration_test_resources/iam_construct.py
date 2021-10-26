from aws_cdk import aws_iam, core


class IAMConstruct(core.Construct):
    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        bucket_arn: str,
        **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
        self.create_oidc_provider()
        self.create_github_action_role(bucket_arn=bucket_arn)

    def create_oidc_provider(self) -> None:
        self.oidc = aws_iam.OpenIdConnectProvider(
            self,
            "github_actions_oidc",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
            thumbprints=["6938fd4d98bab03faadb97b34396831e3780aea1"]
        )

    def create_github_action_role(self, bucket_arn: str) -> None:

        self.github_action_role = aws_iam.Role(
            self,
            "github_actions_role",
            role_name="amplifyios-githubaction-integtest",
            description="Role assumed by GitHub action in the amplify-ios integration test",
            assumed_by=aws_iam.FederatedPrincipal(
                self.oidc.open_id_connect_provider_arn,
                assume_role_action="sts:AssumeRoleWithWebIdentity",
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": "repo:aws-amplify/amplify-ios:*"
                    }
                })
        )

        bucket_resource = bucket_arn + "/testconfiguration/*"
        bucket_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:GetObject", "s3:ListBucket"],
            resources=[bucket_arn, bucket_resource],

        )
        self.github_action_role.add_to_policy(bucket_policy)
