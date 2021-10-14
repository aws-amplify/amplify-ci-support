import * as cdk from '@aws-cdk/core';
import * as path from 'path';
import * as nodejsLambda from '@aws-cdk/aws-lambda-nodejs';
import * as secretmanager from '@aws-cdk/aws-secretsmanager';
import * as iam from '@aws-cdk/aws-iam';
import * as events from '@aws-cdk/aws-events';
import * as target from '@aws-cdk/aws-events-targets';

export class AwsTokenRotationStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const role = new iam.Role(this, 'rotatorLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });
    const githubSecretArnParam = new cdk.CfnParameter(this, "githubSecretArn", {
      noEcho: true,
      type: 'String',
    });

    const crossAccountRole = new cdk.CfnParameter(this, "crossAccountRoleArn", {
      noEcho: true,
      type: 'String',
    })
    const e2eTestRoleArn = new cdk.CfnParameter(this, "e2eTestRoleArn", {
      noEcho: true,
      type: 'String',
    })

    const secret = secretmanager.Secret.fromSecretCompleteArn(this, 'githubSecret', githubSecretArnParam.valueAsString);
    secret.grantRead(role);

    role.addToPolicy(new iam.PolicyStatement({
      actions: ['sts:assumerole'],
      resources: [crossAccountRole.valueAsString]
    }));

    const rotatorFunction = new nodejsLambda.NodejsFunction(this, 'RotatorLambda', {
      entry: path.normalize(path.join(__dirname, 'lambda-handler', 'index.ts')),
      environment: {
        CROSS_ACCOUNT_ROLE_ARN: crossAccountRole.valueAsString,
        GITHUB_TOKEN_ARN: secret.secretArn,
        ROLE_ARN:  e2eTestRoleArn.valueAsString,
      },
      role,
      timeout:  cdk.Duration.minutes(5)

    })

    const eventRule = new events.Rule(this, "FiveHourlySchedule", {
      schedule: events.Schedule.cron({
        hour: '5',
        minute: '30',
      })
    });

    eventRule.addTarget(new target.LambdaFunction(rotatorFunction));
   
  }
}
