import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Alarm, ComparisonOperator, Metric, TreatMissingData, DimensionsMap, Stats } from 'aws-cdk-lib/aws-cloudwatch';

const metricNamespace = "GithubCanaryApps";

// Create the metric and alarms for tracking Github Canary failures.
// These metrics are sent in Github action: amplify-flutter/amplify_canaries
export function createCanaryTestFailureAlarm(scope: Construct) {

  const buildFailureMetric = createMetric(
    "BuildCanaryTestFailure",
    {
      "channel": "stable",
      "label": "Canary Build Failures",
    }
  );

  const E2EAndroidMetric = createMetric(
    "E2ECanaryTestFailure",
    {
      "channel": "stable",
      "platform": "android",
      "label": "E2E Canary Failures",
    }
  );

  const E2EIosMetric = createMetric(
    "E2ECanaryTestFailure",
    {
      "channel": "stable",
      "platform": "ios",
      "label": "E2E Canary Failures",
    }
  );

  createAlarm(scope, `build-canary-test-failure-alarm`, "Build Canary Test Failure Alarm", "Alarm triggered when the Github Action Canaries build step fails", buildFailureMetric);

  createAlarm(scope, `e2e-android-canary-test-failure-alarm`, "E2E Android Canary Test Failure Alarm", "Alarm triggered when the Github Action Canaries E2E android step fails", E2EAndroidMetric);

  createAlarm(scope, `e2e-ios-canary-test-failure-alarm`, "E2E iOS Canary Test Failure Alarm", "Alarm triggered when the Github Action Canaries E2E ios step fails", E2EIosMetric);

  // TODO: Create Github issues as alarm actions

  // TODO: Consider moving to brazil to allow SIM Ticket creation.
  // reason: package 'SIMTicketAlarmAction' is an AWS internal package.

}

function createMetric(metricName: string, dimensions: DimensionsMap): Metric {
  return new Metric({
    metricName,
    namespace: metricNamespace,
    statistic: Stats.MAXIMUM,
    period: Duration.hours(24),
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