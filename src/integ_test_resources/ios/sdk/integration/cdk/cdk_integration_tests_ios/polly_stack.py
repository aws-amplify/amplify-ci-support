from aws_cdk import aws_iam, aws_s3, core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class PollyStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        self.create_bucket(common_stack)

        all_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "polly:DeleteLexicon",
                "polly:GetSpeechSynthesisTask",
                "polly:ListSpeechSynthesisTasks",
                "polly:PutLexicon",
                "polly:StartSpeechSynthesisTask",
                "polly:SynthesizeSpeech",
            ],
            resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    def create_bucket(self, common_stack):
        bucket_name = self.get_bucket_name("output")
        bucket = aws_s3.Bucket(self, "integ_test_polly_output_bucket", bucket_name=bucket_name)
        self._parameters_to_save["s3_output_bucket_name"] = bucket.bucket_name
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{bucket_name}/*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=policy)
