from aws_cdk import aws_secretsmanager, aws_iam, core
from cdk.credential_rotation.iam_construct import IAMConstruct
import cdk.credential_rotation.utils.secretmanager_constants as constants


class SecretManagerConstruct(core.Construct):
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
        iam_construct.lambda_role_add_to_policy(lambda_role_get_secret_policy)

