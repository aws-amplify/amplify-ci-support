from aws_cdk import aws_iam, aws_s3, core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class PollyStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        aws_s3.Bucket(self, "integ_test_polly_output_bucket", bucket_name=self.polly_bucket_name)
        self._parameters_to_save["s3_output_bucket_name"] = self.polly_bucket_name

        s3_output_bucket_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{self.polly_bucket_name}/*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=s3_output_bucket_policy)

        # Per https://docs.aws.amazon.com/polly/latest/dg/security_iam_service-with-iam.html:
        # "Amazon Polly does not support specifying resource ARNs in a policy." This conflicts with
        # documentation
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

    # Ideally we'd do this by simply creating the bucket dynamically, but subsequently referring to
    # the bucket causes a circular reference between the common and polly stacks
    @property
    def polly_bucket_name(self):
        bucket_name = f"integ-test-polly-output-bucket-{self.region}-{self.account}"
        return bucket_name
