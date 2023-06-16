import { assertions, App } from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { GithubCloudwatchCdkStack } from '../lib/github-cloudwatch-cdk-stack';

let template: assertions.Template

beforeAll(() => {
    const app = new App();
    const stack = new GithubWorkflowsCdkStack(app, 'MyTestStack');
    template = Template.fromStack(stack);
})

// example test. To run these tests, uncomment this file along with the
// example resource in lib/github-workflows-cdk-stack.ts
describe('GithubWorkflowsStack', () => {

    it("should have BuildAndRuntimeTestFailure", () => {
        template.hasResourceProperties("AWS::CloudWatch::Alarm", {
            "ComparisonOperator": "GreaterThanThreshold",
            "EvaluationPeriods": 2,
            "ActionsEnabled": false,
            "AlarmActions": [], // Action must be created within AWS Isengard Console
            "AlarmDescription": "Alarm triggered when the Github Action Canaries workflow fails",
            "AlarmName": "¥",
            "DatapointsToAlarm": 2,
            "MetricName": "CanaryTestFailure",
            "Namespace": "GithubCanaryApps",
            "Period": 12000,
            "Statistic": "Maximum",
            "Threshold": 0,
            "TreatMissingData": "missing"
        })
    });
});