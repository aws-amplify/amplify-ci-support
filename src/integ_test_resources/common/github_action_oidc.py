from aws_cdk import core, aws_iam

class GithubActionOIDC(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str):
        super().__init__(scope, construct_id)

        self.provider = aws_iam.OpenIdConnectProvider(self, "Provider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"]
        )

        aws_sdk_ios_integration_test_principal = aws_iam.OpenIdConnectPrincipal(self.provider,
            conditions={
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    "token.actions.githubusercontent.com:sub": "repo:aws-amplify/aws-sdk-ios:environment:IntegrationTest"
                }
            }
        )

        self.aws_sdk_ios_integration_test_role = aws_iam.Role(self, "AwsSDKiOSIntegrationTestOIDCRole",
            assumed_by=aws_sdk_ios_integration_test_principal
        )
