from aws_cdk import(
    core,
    aws_s3
)


from parameter_store import save_string_parameter
from common_stack import CommonStack
from cdk_stack_extension import CDKStackExtension

class S3Stack(CDKStackExtension):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 common_stack: CommonStack,
                 **kwargs) -> None:
        super().__init__(scope,
                         id,
                         **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        bucket = aws_s3.Bucket(
            self, 'ios-v2-s3-tm-testdata'
        )

        save_string_parameter(self,
                              "ios-v2-s3-tm-testdata_bucket_name",
                              bucket.bucket_name)

        common_stack.add_to_common_role_policies(self)