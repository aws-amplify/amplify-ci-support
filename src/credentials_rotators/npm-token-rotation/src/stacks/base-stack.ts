// import * as core from "@aws-cdk/core";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from "aws-cdk-lib/aws-iam";
import { StateMachine } from "aws-cdk-lib/aws-stepfunctions";
import * as sns from "aws-cdk-lib/aws-sns";
import * as secretsManager from "aws-cdk-lib/aws-secretsmanager";
import * as snsSubscriptions from "aws-cdk-lib/aws-sns-subscriptions";
import { SnsAction } from "aws-cdk-lib/aws-cloudwatch-actions";

import { Duration, Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import { SecretDetail } from "../base-types";
import { AccessTokenRotationConfig } from "../config-types";

/**
 * Contains utility functions for NpmTokenRotationStack to use
 */
export class BaseStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);
  }

  protected grantSecretsManagerToAccessLambda = (fn: lambda.IFunction) => {
    const principal = new iam.ServicePrincipal("secretsmanager.amazonaws.com");
    fn.addPermission("invoke_access_to_secretsmanager", { principal });
  };

  protected grantLambdaFunctionToAccessStepFunctions = (
    fn: lambda.IFunction,
    machine: StateMachine
  ) => {
    machine.grantStartExecution(fn);
  };

  protected grantLambdaAccessToRotateSecrets = (
    fn: lambda.IFunction,
    secret: SecretDetail
  ) => {
    if (secret.roleArn) {
      this.grantLambdaToAssumeRolePermission(fn, secret.roleArn);
    } else {
      this.grantLambdaAccessToWriteSecret(fn, secret.arn);
    }
    const actions = secret.roleArn
      ? ["sts:AssumeRole"]
      : [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage",
        ];
    const resources = secret.roleArn ? [secret.roleArn] : [secret.arn];

    fn.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        resources,
        actions,
      })
    );

    fn.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        resources: ["*"],
        actions: ["secretsmanager:GetRandomPassword"],
      })
    );
  };

  protected grantLambdaAccessToSecrets = (
    fn: lambda.IFunction,
    secretDetails: Readonly<SecretDetail[]>
  ) => {
    for (const secretDetail of secretDetails) {
      if (secretDetail.roleArn) {
        this.grantLambdaToAssumeRolePermission(fn, secretDetail.roleArn);
      } else {
        this.grantLambdaAccessToReadSecret(fn, secretDetail.arn);
      }
    }
  };

  protected configureSecretRotation = (
    fn: lambda.IFunction,
    config: Readonly<SecretDetail>,
    duration: Duration
  ) => {
    const secret = secretsManager.Secret.fromSecretCompleteArn(
      this,
      `${config.arn}-${config.secretKey}`,
      config.arn
    );
    secret.addRotationSchedule(`${config.arn}-${config.secretKey}-rotator`, {
      automaticallyAfter: duration,
      rotationLambda: fn,
    });
  };

  protected enableCloudWatchAlarmNotification = (
    fn: lambda.IFunction,
    name: string,
    config: Readonly<AccessTokenRotationConfig>
  ) => {
    const topicId = `${name}_alarm_sns_topic`;
    const topic = new sns.Topic(this, topicId);
    for (const email of config.alarmSubscriptions) {
      topic.addSubscription(new snsSubscriptions.EmailSubscription(email));
    }

    const alarm = fn.metricErrors().createAlarm(this, `${name}_error_alarm`, {
      threshold: 1,
      evaluationPeriods: 1,
      alarmName: `${name}-alarm`,
    });
    alarm.addAlarmAction(new SnsAction(topic));
  };

  protected grantLambdaToAssumeRolePermission = (
    fn: lambda.IFunction,
    roleArn: string
  ): void => {
    fn.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        resources: [roleArn],
        actions: ["sts:AssumeRole"],
      })
    );
  };

  protected grantLambdaAccessToReadSecret = (
    fn: lambda.IFunction,
    secretArn: string
  ): void => {
    fn.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        resources: [secretArn],
        actions: ["secretsmanager:GetSecretValue"],
      })
    );
  };

  protected grantLambdaAccessToWriteSecret = (
    fn: lambda.IFunction,
    secretArn: string
  ): void => {
    fn.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        resources: [secretArn],
        actions: [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage",
        ],
      })
    );
  };
}
