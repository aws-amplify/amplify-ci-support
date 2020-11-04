from aws_cdk import (
    aws_cloudtrail,
    aws_cloudwatch,
    aws_logs,
    aws_s3,
    core
)

class AccountBootstrap(core.Stack):
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Setup CloudTrail to stream logs to CloudWatch logs
        log_group=aws_logs.LogGroup(self, "CloudTrailLogs", 
            log_group_name="CloudTrailLogs",
            retention=aws_logs.RetentionDays.TWO_WEEKS)
        aws_cloudtrail.Trail(self, "OpsTrail",
            cloud_watch_log_group=log_group, 
            cloud_watch_logs_retention=aws_logs.RetentionDays.TWO_WEEKS,
            send_to_cloud_watch_logs=True, 
            trail_name="OpsTrail")

        self.config_source_bucket = aws_s3.Bucket(self, "AmplifyConfigBucket", bucket_name=f"amplify-ci-assets-{self.account}", removal_policy=core.RemovalPolicy.DESTROY)
        