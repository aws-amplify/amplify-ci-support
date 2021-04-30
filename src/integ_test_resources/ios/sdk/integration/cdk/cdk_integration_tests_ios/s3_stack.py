from aws_cdk import aws_iam, aws_s3, core
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class S3Stack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        bucket_name_prefix = self.create_dynamic_bucket_prefix()
        bucket_name_basic = self.create_basic_bucket()
        bucket_name_periods = self.create_period_bucket()
        bucket_name_transfer_acceleration = self.create_transfer_accelerated_bucket()

        bucket_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:*"],
            resources=[
                f"arn:aws:s3:::{bucket_name_prefix}*",
                f"arn:aws:s3:::{bucket_name_prefix}*/*",
                f"arn:aws:s3:::{bucket_name_basic}",
                f"arn:aws:s3:::{bucket_name_basic}/*",
                f"arn:aws:s3:::{bucket_name_periods}",
                f"arn:aws:s3:::{bucket_name_periods}/*",
                f"arn:aws:s3:::{bucket_name_transfer_acceleration}",
                f"arn:aws:s3:::{bucket_name_transfer_acceleration}/*",
            ],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=bucket_resources_policy)

        all_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["s3:ListAllMyBuckets"], resources=["*"]
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    def create_dynamic_bucket_prefix(self) -> str:
        bucket_name_prefix = self.get_bucket_name("")
        self._parameters_to_save["bucket_name_prefix"] = bucket_name_prefix
        return bucket_name_prefix

    def create_basic_bucket(self) -> str:
        bucket_name = self.get_bucket_name("basic")
        aws_s3.Bucket(
            self,
            "integ_test_s3_bucket_basic",
            bucket_name=bucket_name,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        self._parameters_to_save["bucket_name_basic"] = bucket_name
        return bucket_name

    def create_period_bucket(self) -> str:
        bucket_name = self.get_bucket_name("period.test")
        aws_s3.Bucket(
            self,
            "integ_test_s3_bucket_periods",
            bucket_name=bucket_name,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        self._parameters_to_save["bucket_name_with_periods"] = bucket_name
        return bucket_name

    def create_transfer_accelerated_bucket(self) -> str:
        bucket_name = self.get_bucket_name("accel")
        # As of this writing (2020-05-11), The Bucket object does not expose transfer acceleration
        bucket = aws_s3.CfnBucket(
            self,
            "integ_test_s3_bucket_transfer_acceleration",
            bucket_name=bucket_name,
            accelerate_configuration={"accelerationStatus": "Enabled"},
        )
        self._parameters_to_save["bucket_name_transfer_acceleration"] = bucket_name
        bucket.apply_removal_policy(core.RemovalPolicy.DESTROY)
        return bucket_name
