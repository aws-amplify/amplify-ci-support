from aws_cdk import core as cdk
from cdk.credential_rotation.events_construct import EventsConstruct
from cdk.credential_rotation.iam_construct import IAMConstruct
from cdk.credential_rotation.lambda_construct import LambdaConstruct
from cdk.credential_rotation.secretsmanager_construct import SecretsManagerConstruct
from cdk.credential_rotation.cloudwatch_construct import CloudWatchConstruct


class CredentialRotationStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        bucket_name: str,
        bucket_arn: str,
        cloudfront_distribution_id: str,
        cloudfront_arn: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        iam_construct = IAMConstruct(
            self, "credential_rotation_iam", bucket_arn=bucket_arn, cloudfront_arn=cloudfront_arn
        )
        secretsmanager_construct = SecretsManagerConstruct(
            self, "credential_rotation_secret", iam_construct=iam_construct
        )
        lambda_construct = LambdaConstruct(
            self,
            "credential_rotation_lambda",
            bucket_name=bucket_name,
            cloudfront_distribution_id=cloudfront_distribution_id,
            iam_construct=iam_construct,
            secretsmanager_construct=secretsmanager_construct,
        )

        EventsConstruct(self, "credential_rotation_event", lambda_construct=lambda_construct)
        CloudWatchConstruct(
            self, "credential_rotation_cloudwatch", lambda_construct=lambda_construct
        )
