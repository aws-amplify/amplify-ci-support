from aws_cdk import aws_iam, aws_kinesisfirehose, aws_s3, core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class FirehoseStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        delivery_bucket = aws_s3.Bucket(
            self,
            "integ-test-firehose-delivery-bucket"
        )
        delivery_role = aws_iam.Role(
            self,
            "integ-test-firehose-delivery-role",
            assumed_by=aws_iam.ServicePrincipal("firehose.amazonaws.com")
        )
        wic_provider_test_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW, actions=["translate:TranslateText"], resources=["*"]
            )
        )

        firehose = aws_kinesisfirehose.CfnDeliveryStream(
            self,
            "integ-test-firehose",
            s3_destination_configuration={
                "bucketArn": delivery_bucket.bucket_arn,
                "bufferingHints": {
                     "intervalInSeconds": 60,
                     "sizeInMBs": 50
                },
                "compressionFormat": "ZIP"
            }
        )
        firehose_arn = firehose.get_att("Arn").to_string()

        all_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["firehose:DescribeLoadBalancers"],
            resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

        deliverystream_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["firehose:PutRecordBatch"],
            resources=[firehose_arn],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=deliverystream_policy)

        self._parameters_to_save["firehose_arn"] = firehose_arn
        self.save_parameters_in_parameter_store(Platform.IOS)
