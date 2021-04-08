import cdk.credential_rotation.utils.secretmanager_constants as constants
from aws_cdk import aws_iam, aws_secretsmanager, core
from cdk.credential_rotation.iam_construct import IAMConstruct


class SecretsManagerConstruct(core.Construct):
    def __init__(
        self, scope: core.Construct, construct_id: str, iam_construct: IAMConstruct, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.circleci_api_key = aws_secretsmanager.Secret(
            self,
            "circleCI_API_key",
            description="CircleCI API key used by credential rotator lambda",
            secret_name=constants.CIRCLECI_API_KEY,
        )

        lambda_role_get_secret_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["secretsmanager:GetSecretValue"],
            resources=[self.circleci_api_key.secret_full_arn],
        )
        iam_construct.add_policy_to_lambda_role(lambda_role_get_secret_policy)
