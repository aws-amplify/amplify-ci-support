import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CanaryTestFailureAlarm } from './CanaryTestFailureAlarm';

export class GithubCloudwatchCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // TODO(kylechen): 06/ Consolidate role creation into this CDK code.
    // It's currently performed in a separate CloudFormation template:
    // https://github.com/aws-amplify/amplify-ci-support/blob/main/src/integ_test_resources/flutter/amplify/cloudformation_template.yaml

    new CanaryTestFailureAlarm(this, 'CanaryTestFailureAlarm');

  }
}
