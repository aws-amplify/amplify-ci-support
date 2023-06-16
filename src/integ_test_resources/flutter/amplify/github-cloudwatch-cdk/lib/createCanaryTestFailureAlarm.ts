import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Alarm, ComparisonOperator, GraphWidget, Metric, TextWidget, TreatMissingData } from 'aws-cdk-lib/aws-cloudwatch';

// Create the metric and alarms for tracking Github Canary failures.
// These metrics are sent in Github action: amplify-flutter/amplify_canaries
export function createCanaryTestFailureAlarm(scope: Construct) {
  const createCanaryTestFailureMetric = new Metric({
    metricName: "CanaryTestFailure",
    namespace: "GithubCanaryApps",
    statistic: "Max",
    // TODO(kylechen): DO NOT MERGE until clarified runtime frequency
    // GithubAction's Mac minutes multiplier is x10 vs. Unix
    period: Duration.minutes(200),
  });

  const createCanaryTestFailureAlarm = new Alarm(scope, `create-canary-test-failure-alarm`, {
    alarmName: "Create Canary Test Failure Alarm",
    alarmDescription: `Alarm triggered when the Github Action Canaries workflow fails`,
    metric: createCanaryTestFailureMetric,
    threshold: 0,
    evaluationPeriods: 2,
    datapointsToAlarm: 2,
    comparisonOperator: ComparisonOperator.GREATER_THAN_THRESHOLD,
    actionsEnabled: true,
    treatMissingData: TreatMissingData.MISSING,
  });

  // TODO(kylechen): Consider moving to brazil to allow SIM Ticket creation.
  // reason: package 'SIMTicketAlarmAction' is an AWS internal package.
  /*
  import { SIMTicketAlarmAction, Severity } from "@amzn/sim-ticket-cdk-constructs";
  const severity = Severity.SEV2_5;
  createCanaryTestFailureAlarm.addAlarmAction(new SIMTicketAlarmAction({
    severity,
    dedupe: `github-build-and-runtime-test-failure-alarm-${stage}`,
    summary: "There's a failure on Github Actions when running 'Run and Test Builds' workflow.",
    details: "Check what failed -> https://github.com/aws-amplify/amplify-ui/actions/workflows/build-and-runtime-test.yml",
    ...CTI_GROUP
  }));
  */
}