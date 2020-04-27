from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import core


class CloudwatchStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 circleci_execution_role: iam.Role,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        log_group = logs.LogGroup(self, 'android-integ-test-log-group',
                                  log_group_name='com/amazonaws/tests')

        circleci_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["cloudwatch:*"], resources=["*"]))
