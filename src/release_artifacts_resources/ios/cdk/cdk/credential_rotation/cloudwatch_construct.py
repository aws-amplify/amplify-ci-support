from aws_cdk import aws_cloudwatch, core
from cdk.credential_rotation.lambda_construct import LambdaConstruct


class CloudWatchConstruct(core.Construct):
    def __init__(
        self, scope: core.Construct, construct_id: str, lambda_construct: LambdaConstruct, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_error_metrics = lambda_construct.credential_rotator.metric_errors(
            period=core.Duration.minutes(5)
        )
        aws_cloudwatch.Alarm(
            self,
            "credential_rotator_error_metrics",
            metric=lambda_error_metrics,
            evaluation_periods=1,
            threshold=2,
            alarm_description="""
            Alarm if the number of errors in credential rotator increase to a threshold
            """
        )
