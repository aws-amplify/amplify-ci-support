import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Alarm, ComparisonOperator, Metric, TreatMissingData, DimensionsMap, Stats } from 'aws-cdk-lib/aws-cloudwatch';

const metricNamespace = "GithubCanaryApps";

// Create the metric and alarms for tracking Github Canary failures.
// These metrics are sent in Github action: amplify-flutter/amplify_canaries
export function createCanaryTestFailureAlarm(scope: Construct) {

  const BuildFailureStableMetric = createMetric(
    "BuildCanaryTestFailure",
    {
      "channel": "stable",
      "label": "CanaryBuildFailures",
    }
  );

  const E2EAndroidStableMetric = createMetric(
    "E2ECanaryTestFailure",
    {
      "channel": "stable",
      "platform": "android",
      "label": "E2ECanaryFailures",
    }
  );

  const E2EIosStableMetric =

    "E2ECanaryTestFailure",
    {
      "channel": "stable",
      "platform": "ios",
      "label": "E2ECanaryFailures",
    }
  );

  createAlarm(scope, `build-canary-test-failure-alarm`, "Build Canary (stable)", "Alarm triggered when the Github Action Canaries build step fails", BuildFailureStableMetric);

  createAlarm(scope, `e2e-android-canary-test-failure-alarm`, "E2E Android Canary (stable)", "Alarm triggered when the Github Action Canaries E2E android step fails", E2EAndroidStableMetric);

  createAlarm(scope, `e2e-ios-canary-test-failure-alarm`, "E2E iOS Canary (stable)", "Alarm triggered when the Github Action Canaries E2E iOS step fails", E2EIosStableMetric);

  // TODO: Create Github issues as alarm actions

  // TODO: Consider moving to brazil to allow SIM Ticket creation.
  // reason: package 'SIMTicketAlarmAction' is an AWS internal package.

}

function createMetric(metricName: string, dimensions: DimensionsMap): Metric {
  return new Metric({
    metricName,
    namespace: metricNamespace,
    statistic: Stats.MAXIMUM,
    period: Duration.minutes(5),
    dimensionsMap: dimensions,
  });
}

function createAlarm(scope: Construct, id: string, alarmName: string, alarmDescription: string, metric: Metric) {
  return new Alarm(scope, id, {
    alarmName: alarmName,
    alarmDescription: alarmDescription,
    metric: metric,
    threshold: 0,
    evaluationPeriods: 1,
    datapointsToAlarm: 1,
    comparisonOperator: ComparisonOperator.GREATER_THAN_THRESHOLD,
    actionsEnabled: true,
    treatMissingData: TreatMissingData.IGNORE,
  });
}