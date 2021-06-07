import json
import os

from aws_cdk import aws_events, aws_events_targets, core
from cdk.credential_rotation.lambda_construct import LambdaConstruct


class EventsConstruct(core.Construct):
    def __init__(
        self, scope: core.Construct, construct_id: str, lambda_construct: LambdaConstruct, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        file_name = os.path.join(os.path.dirname(__file__), "./utils/lambda_event_data.json")
        event_data_file = open(file_name, "r")
        event_data = json.loads(event_data_file.read())
        rule_target = aws_events.RuleTargetInput.from_object(event_data)

        target = aws_events_targets.LambdaFunction(
            handler=lambda_construct.credential_rotator, event=rule_target
        )
        schedule_duration = core.Duration.hours(2)

        aws_events.Rule(
            self,
            "credential_rotator_event",
            rule_name="credential_rotation_lambda_trigger",
            description="Event to trigger CircleCI credential rotation every two hours",
            schedule=aws_events.Schedule.rate(schedule_duration),
            targets=[target],
        )
