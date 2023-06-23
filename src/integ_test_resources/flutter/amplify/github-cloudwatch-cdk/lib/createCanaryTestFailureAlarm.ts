import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Alarm, ComparisonOperator, GraphWidget, Metric, TextWidget, TreatMissingData } from 'aws-cdk-lib/aws-cloudwatch';

// Create the metric and alarms for tracking Github Canary failures.
// These metrics are sent in Github action: amplify-flutter/amplify_canaries
export function createCanaryTestFailureAlarm(scope: Construct) {

  const buildFailureMetric = new Metric({
    metricName: "BuildCanaryTestFailure",
    namespace: "GithubCanaryApps",
    statistic: "Max",
    period: Duration.hours(24),
    dimensions: {
        "channel" : "stable"
    }
  });

  const e2eAndroidMetric = new Metric({
    metricName: "e2eCanaryTestFailure",
    namespace: "GithubCanaryApps",
    statistic: "Max",
    period: Duration.hours(24),
    dimensions: {
        "channel" : "stable",
        "platform" : "android"
    }
  });

  const e2eIosMetric = new Metric({
    metricName: "e2eCanaryTestFailure",
    namespace: "GithubCanaryApps",
    statistic: "Max",
    period: Duration.hours(24),
    dimensions: {
        "channel" : "stable",
        "platform" : "ios"
    }
  });

  // TODO(kylechen): Create metrics for channel: beta
  // TODO(kylehcen): Create Github issues as alarm actions

  const buildFailureAlarm = new Alarm(scope, `build-canary-test-failure-alarm`, {
    alarmName: "Build Canary Test Failure Alarm",
    alarmDescription: `Alarm triggered when the Github Action Canaries build step fails`,
    metric: buildFailureMetric,
    threshold: 0,
    evaluationPeriods: 1,
    datapointsToAlarm: 1,
    comparisonOperator: ComparisonOperator.GREATER_THAN_THRESHOLD,
    actionsEnabled: true,
    treatMissingData: TreatMissingData.MISSING,
  });

  const e2eAndroidMetric = new Alarm(scope, `e2e-android-canary-test-failure-alarm`, {
    alarmName: "e2e Android Canary Test Failure Alarm",
    alarmDescription: `Alarm triggered when the Github Action Canaries e2e android step fails`,
    metric: e2eAndroidMetric,
    threshold: 0,
    evaluationPeriods: 1,
    datapointsToAlarm: 1,
    comparisonOperator: ComparisonOperator.GREATER_THAN_THRESHOLD,
    actionsEnabled: true,
    treatMissingData: TreatMissingData.MISSING,
  });

  const e2eIosMetric = new Alarm(scope, `e2e-ios-canary-test-failure-alarm`, {
    alarmName: "e2e iOS Canary Test Failure Alarm",
    alarmDescription: `Alarm triggered when the Github Action Canaries e2e ios step fails`,
    metric: e2eIosMetric,
    threshold: 0,
    evaluationPeriods: 1,
    datapointsToAlarm: 1,
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