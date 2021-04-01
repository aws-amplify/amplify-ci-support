import cdk.credential_rotation.utils.lambda_constants as lambda_constants
from aws_cdk import aws_lambda, aws_lambda_python, core
from cdk.credential_rotation.iam_construct import IAMConstruct


class LambdaConstruct(core.Construct):
    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        iam_construct: IAMConstruct,
        secret_arn: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.credential_rotator = aws_lambda_python.PythonFunction(
            self,
            "credential_rotation_lambda",
            entry="cdk/credential_rotation/lambda_functions/",
            index="credential_rotator.py",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            role=iam_construct.lambda_role,
            timeout=core.Duration.minutes(5),
            description="Credential rotation script for the AWS iOS SDK CircleCI pipeline",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.DESTROY
            ),
        )
        self.credential_rotator.add_environment(
            lambda_constants.CIRCLECI_CONFIG_SECRET_ENV, secret_arn
        )

        self.credential_rotator.add_environment(
            lambda_constants.CIRCLECI_EXECUTION_ROLE_ENV,
            iam_construct.circleci_release_role.role_arn,
        )

        self.credential_rotator.add_environment(
            lambda_constants.IAM_USERNAME_ENV, iam_construct.circleci_user.user_name
        )

        self.credential_rotator.add_environment(lambda_constants.GITHUB_PROJECT_PATH_ENV, "aws-amplify/aws-sdk-ios")
