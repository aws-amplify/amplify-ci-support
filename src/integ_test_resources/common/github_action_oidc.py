from aws_cdk import aws_iam as iam
from constructs import Construct

class GithubActionOIDC(Construct):
    def __init__(self, scope: Construct, construct_id: str):
        super().__init__(scope, construct_id)

        self.provider = iam.OpenIdConnectProvider(self, "provider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"]
        )

        aws_sdk_ios_integration_test_principal = iam.OpenIdConnectPrincipal(self.provider,
            conditions={
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    "token.actions.githubusercontent.com:sub": "repo:aws-amplify/aws-sdk-ios:environment:IntegrationTest"
                }
            }
        )

        self.aws_sdk_ios_integration_test_role = iam.Role(
            self,
            "aws_sdk_ios_integration_test_role",
            assumed_by=aws_sdk_ios_integration_test_principal
        )
