import hashlib
import os

from aws_cdk import core
from boto3.session import Session

from common.parameter_store import save_string_parameter
from common.platforms import Platform


class RegionAwareStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region: bool
        self._parameters_to_save = {}
        self._id = id

    def is_service_supported_in_region(
        self, service_name: str = None, region_name: str = None
    ) -> bool:

        boto3_session = Session()
        if region_name is None:
            region_name = os.environ["AWS_DEFAULT_REGION"]

        if service_name is None:
            service_name = self.stack_name

        supported_regions_for_service = boto3_session.get_available_regions(service_name)
        service_supported_in_region = region_name in supported_regions_for_service
        return service_supported_in_region

    def are_services_supported_in_region(
        self, service_names: list, region_name: str = None
    ) -> bool:

        services_supported_in_region = True
        for service_name in service_names:
            services_supported_in_region = (
                services_supported_in_region
                and self.is_service_supported_in_region(
                    service_name=service_name, region_name=region_name
                )
            )
        return services_supported_in_region

    def save_parameters_in_parameter_store(self, platform: Platform) -> None:

        for parameter_name, parameter_value in self.parameters_to_save.items():
            save_string_parameter(self, parameter_name, parameter_value, platform=platform)

    def add_dependencies_with_region_filter(self, stacks_to_add: list) -> None:
        for stack in stacks_to_add:
            if stack.supported_in_region:
                self.add_dependency(stack)

    @property
    def supported_in_region(self) -> bool:
        return self._supported_in_region

    @property
    def parameters_to_save(self) -> dict:
        return self._parameters_to_save

    @property
    def id(self) -> str:
        return self._id

    def get_bucket_name(self, tag) -> str:
        """
        Returns a string to be used as the name for an S3 bucket. As of this writing (2020-05-12),
        directly referring to bucket ARNs and names in stacks causes circular dependencies between
        common and the bucket-owning stack.

        Usage example:
            bucket_name = self.get_bucket_name("media_upload")
            bucket = aws_s3.Bucket(self, "integ_test_transcribe_bucket", name=bucket_name)

            policy = aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=["s3:PutObject"],
                resources=[f"arn:aws:s3:::{self.bucket_name}/*"],
            )
            common_stack.add_to_common_role_policies(self, policy_to_add=policy)

        :return: a string to be used for a bucket name
        """
        bucket_tag = f"{self.region}-{self.account}-{tag}"
        bucket_hash = hashlib.md5(bucket_tag.encode()).hexdigest()
        bucket_name = f"integ-test-{self.id}-{tag}-{bucket_hash}"
        return bucket_name
