import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Alarm, ComparisonOperator, Metric, TreatMissingData, DimensionsMap, Stats } from 'aws-cdk-lib/aws-cloudwatch';

// Create the metric and alarms for tracking Github Canary failures.
// These metrics are sent in Github action: amplify-flutter/amplify_canaries
export class CanaryTestFailureAlarm extends Construct {

  private static metricNamespace = 'GithubCanaryApps';

  constructor(scope: Construct, id: string) {
    super(scope, id);

    const buildFailureStableMetric = this.createMetric(
      'BuildCanaryTestFailure',
      'CanaryBuildFailures',
      {
        channel: 'stable',
      }
    );

    const e2eAndroidStableMetric = this.createMetric(
      'E2ECanaryTestFailure',
      'E2ECanaryFailures',
      {
        channel: 'stable',
        platform: 'android',
      }
    );

    const e2eIosStableMetric = this.createMetric(
      'E2ECanaryTestFailure',
      'E2ECanaryFailures',
      {
        channel: 'stable',
        platform: 'ios',
      }
    );

    this.createAlarm(
      `build-canary-test-failure-alarm`,
      'Build Canary (stable)',
      'Alarm triggered when the Github Action Canaries build step fails',
      buildFailureStableMetric
    );

    this.createAlarm(
      `e2e-android-canary-test-failure-alarm`,
      'E2E Android Canary (stable)',
      'Alarm triggered when the Github Action Canaries E2E android step fails',
      e2eAndroidStableMetric
    );

    this.createAlarm(
      `e2e-ios-canary-test-failure-alarm`,
      'E2E iOS Canary (stable)',
      'Alarm triggered when the Github Action Canaries E2E iOS step fails',
      e2eIosStableMetric
    );

    // TODO: Create Github issues as alarm actions

    // TODO: Consider moving to brazil to allow SIM Ticket creation.
    // reason: package 'SIMTicketAlarmAction' is an AWS internal package.
  }

  private createMetric(metricName: string, label: string, dimensions: DimensionsMap): Metric {
    return new Metric({
      metricName,
      namespace: CanaryTestFailureAlarm.metricNamespace,
      statistic: Stats.MAXIMUM,
      period: Duration.hours(1),
      dimensionsMap: dimensions,
      label: label,
    });
  }

  private createAlarm(id: string, alarmName: string, alarmDescription: string, metric: Metric) {
    return new Alarm(this, id, {
      alarmName,
      alarmDescription,
      metric,
      threshold: 0,
      evaluationPeriods: 1,
      datapointsToAlarm: 1,
      comparisonOperator: ComparisonOperator.GREATER_THAN_THRESHOLD,
      actionsEnabled: true,
      treatMissingData: TreatMissingData.IGNORE,
    });
  }
}