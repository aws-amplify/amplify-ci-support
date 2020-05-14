from aws_cdk import aws_iam, aws_s3, core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class TranscribeStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        all_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "transcribe:CreateVocabulary",
                "transcribe:DeleteVocabulary",
                "transcribe:GetTranscriptionJob",
                "transcribe:GetVocabulary",
                "transcribe:ListTranscriptionJobs",
                "transcribe:ListVocabularies",
                "transcribe:StartStreamTranscriptionWebSocket",
                "transcribe:StartTranscriptionJob",
            ],
            resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

        self.create_bucket(common_stack)

        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    def create_bucket(self, common_stack):
        bucket_name = self.get_bucket_name("media")
        bucket = aws_s3.Bucket(
            self, "integ_test_transcribe_bucket", bucket_name=bucket_name, removal_policy="DESTROY"
        )
        self._parameters_to_save["bucket_name"] = bucket.bucket_name
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:DeleteObject", "s3:GetObject", "s3:PutObject"],
            resources=[f"arn:aws:s3:::{bucket_name}/*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=policy)
