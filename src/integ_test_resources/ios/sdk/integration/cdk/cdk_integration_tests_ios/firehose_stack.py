from aws_cdk import aws_iam, aws_kinesisfirehose, aws_logs, aws_s3, core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class FirehoseStack(RegionAwareStack):
    LOG_GROUP_NAME = "integ_test_firehose_log_group"
    LOG_STREAM_NAME = "integ_test_firehose_log_stream"

    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        delivery_bucket = self.create_s3_delivery_bucket()
        self.create_log_group_and_stream()
        firehose_role_arn = self.create_firehose_role(delivery_bucket)

        firehose = self.create_firehose(delivery_bucket, firehose_role_arn)
        firehose_stream_name = firehose.ref
        self._parameters_to_save["firehose_stream_name"] = firehose_stream_name

        self.create_test_policies(common_stack)

        self.save_parameters_in_parameter_store(Platform.IOS)

    def create_s3_delivery_bucket(self) -> aws_s3.Bucket:
        delivery_bucket = aws_s3.Bucket(
            self, "integ_test_firehose_delivery_bucket", removal_policy="DESTROY"
        )
        return delivery_bucket

    def create_log_group_and_stream(self) -> aws_logs.LogGroup:
        log_group = aws_logs.LogGroup(
            self,
            "integ_test_firehose_delivery_log_group",
            log_group_name=FirehoseStack.LOG_GROUP_NAME,
        )
        aws_logs.LogStream(
            self,
            "integ_test_firehose_delivery_log_stream",
            log_group=log_group,
            log_stream_name=FirehoseStack.LOG_STREAM_NAME,
        )
        return log_group

    def create_firehose_role(self, delivery_bucket) -> str:
        """
        Creates an IAM role to allow Kinesis to deliver records to S3, per
        https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html

        :param delivery_bucket: The destination bucket
        :return: IAM Role ARN
        """
        firehose_role = aws_iam.Role(
            self,
            "integ_test_firehose_delivery_role",
            assumed_by=aws_iam.ServicePrincipal("firehose.amazonaws.com"),
        )

        firehose_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "s3:AbortMultipartUpload",
                    "s3:GetBucketLocation",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:PutObject",
                ],
                resources=[delivery_bucket.bucket_arn, f"{delivery_bucket.bucket_arn}/*"],
            )
        )

        firehose_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "kinesis:DescribeStream",
                    "kinesis:GetShardIterator",
                    "kinesis:GetRecords",
                    "kinesis:ListShards",
                ],
                resources=[f"arn:aws:kinesis:{self.region}:{self.account}:stream/*"],
            )
        )

        log_stream_arn = ":".join(
            [
                "arn:aws:logs",
                self.region,
                self.account,
                "log-group",
                FirehoseStack.LOG_GROUP_NAME,
                "log-stream",
                FirehoseStack.LOG_STREAM_NAME,
            ]
        )
        firehose_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=["logs:PutLogEvents"],
                resources=[log_stream_arn],
            )
        )
        return firehose_role.role_arn

    def create_firehose(
        self, delivery_bucket, firehose_role_arn
    ) -> aws_kinesisfirehose.CfnDeliveryStream:
        """
        Creates a Firehose DeliveryStream configured to deliver to the S3 Bucket `delivery_bucket`,
        and log errors to a log stream named 'S3Delivery' in `log_group`. Firehose will adopt the
        role specified in `firehose_role_arn`.

        :param delivery_bucket: The delivery destination bucket for the Firehose
        :param firehose_role_arn: The role to adopt
        :return: a CfnDeliveryStream
        """
        firehose = aws_kinesisfirehose.CfnDeliveryStream(
            self,
            "integ_test_firehose",
            extended_s3_destination_configuration={
                "bucketArn": delivery_bucket.bucket_arn,
                "bufferingHints": {"intervalInSeconds": 60, "sizeInMBs": 50},
                "compressionFormat": "ZIP",
                "roleArn": firehose_role_arn,
                "cloudWatchLoggingOptions": {
                    "enabled": True,
                    "logGroupName": FirehoseStack.LOG_GROUP_NAME,
                    "logStreamName": FirehoseStack.LOG_STREAM_NAME,
                },
            },
        )
        return firehose

    def create_test_policies(self, common_stack):
        all_resources_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["firehose:ListDeliveryStreams"], resources=["*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=all_resources_policy)

        deliverystream_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["firehose:PutRecord", "firehose:PutRecordBatch"],
            resources=[f"arn:aws:firehose:{self.region}:{self.account}:deliverystream/*"],
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=deliverystream_policy)
