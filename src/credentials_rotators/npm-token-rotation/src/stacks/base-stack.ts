import * as core from "@aws-cdk/core";
import * as lambda from "@aws-cdk/aws-lambda";
import * as iam from "@aws-cdk/aws-iam";
import * as secretsManager from "@aws-cdk/aws-secretsmanager";
import * as sns from "@aws-cdk/aws-sns";
import * as snsSubscriptions from "@aws-cdk/aws-sns-subscriptions";
import { SecretDetail, AccessTokenRotationConfig } from "./types";
import { StateMachine } from "@aws-cdk/aws-stepfunctions";

type BaseStackProps = core.StackProps & {};

export class BaseStack extends core.Stack {
  constructor(scope: core.Construct, id: string, props: core.StackProps = {}) {
    super(scope, id, props);
  }

  protected grantSecretsManagerToAccessLambda = (fn: lambda.IFunction) => {
    const principal = new iam.ServicePrincipal("secretsmanager.amazonaws.com");
    fn.addPermission("invoke_access_to_secretsmanager", { principal });
  };

  protected grantLambdaFunctionToAccessStepFunctions = (fn: lambda.IFunction, machine: StateMachine) => {
    machine.grantStartExecution(fn);
  }

  protected grantLambdaAccessToRotateSecrets = (
    fn: lambda.IFunction,
    secret: SecretDetail
  ) => {
    fn.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        resources: [secret.arn],
        actions: [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage",
        ],
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
    secreteArns: Readonly<string[]>
  ) => {
    for (const secreteArn of secreteArns) {
      fn.addToRolePolicy(
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          resources: [secreteArn],
          actions: ["secretsmanager:GetSecretValue"],
        })
      );
    }
  };

  protected configureSecretRotation = (
    fn: lambda.IFunction,
    config: Readonly<SecretDetail>,
    duration: core.Duration
  ) => {
    const secret = secretsManager.Secret.fromSecretCompleteArn(
      this,
      `${config.arn}-${config.secretKey}`,
      config.arn
    );
    secret.addRotationSchedule(
      `${config.arn}-${config.secretKey}-rotator`,
      {
        automaticallyAfter: duration,
        rotationLambda: fn,
      }
    );
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

    fn.metricErrors().createAlarm(this, `${name}_error_alarm`, {
      threshold: 1,
      evaluationPeriods: 1,
    });
  };
}
