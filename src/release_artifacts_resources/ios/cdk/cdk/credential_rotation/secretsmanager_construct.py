import cdk.credential_rotation.utils.secretmanager_constants as constants
from aws_cdk import aws_iam, aws_secretsmanager, core
from cdk.credential_rotation.iam_construct import IAMConstruct


class SecretsManagerConstruct(core.Construct):
    def __init__(
        self, scope: core.Construct, construct_id: str, iam_construct: IAMConstruct, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.circleci_aws_ios_sdk_api_key = aws_secretsmanager.Secret(
            self,
            "circleCI_AWS_iOS_SDK_API_key",
            description="CircleCI API key used by credential rotator lambda for AWS iOS SDK",
            secret_name=constants.CIRCLECI_AWS_IOS_SDK_API_KEY,
        )
        self.circleci_aws_ios_sdk_spm_api_key = aws_secretsmanager.Secret(
            self,
            "circleCI_AWS_iOS_SDK_SPM_API_key",
            description="CircleCI API key used by credential rotator lambda for AWS iOS SDK SPM",
            secret_name=constants.CIRCLECI_AWS_IOS_SDK_SPM_API_KEY,
        )
        self.github_release_api_key = aws_secretsmanager.Secret(
            self,
            "github_release_api_key",
            description="""GitHub username and API token for CircleCI to access
             the aws-sdk-ios-spm repo to post PRs, merge from release to main
             """,
            secret_name=constants.GITHUB_SPM_RELEASE_API_TOKEN,
        )

        lambda_role_get_secret_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["secretsmanager:GetSecretValue"],
            resources=[
                self.circleci_aws_ios_sdk_api_key.secret_full_arn,
                self.circleci_aws_ios_sdk_spm_api_key.secret_full_arn,
                self.github_release_api_key.secret_full_arn,
            ],
        )
        iam_construct.add_policy_to_lambda_role(lambda_role_get_secret_policy)
