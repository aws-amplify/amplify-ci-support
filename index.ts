import events = require("@aws-cdk/aws-events");
import targets = require("@aws-cdk/aws-events-targets");
import lambda = require("@aws-cdk/aws-lambda");
import iam = require("@aws-cdk/aws-iam");
import sns = require("@aws-cdk/aws-sns");
import snsSubscriptions = require("@aws-cdk/aws-sns-subscriptions");
import cdk = require("@aws-cdk/core");
import * as fs from "fs-extra";
import { Duration } from "@aws-cdk/core";
const TOKEN_TTL_HOURS = 5;
const LAMBDA_FREQUENCY = "rate(1 hour)";
const LAMBDA_NAME = "RotateE2eAwsToken";
const CREATE_ACCESS_KEY_TIMEOUT = 10000;

type E2eTokenRotationConfig = {
  circleCiToken: {
    arn: string;
    secretKey: string;
  };
  circleCiConfig: {
    type: "Context";
    contextName: string;
    slug: string;
    secretKeyIdVariableName: string;
    secretKeyVariableName: string;
  };
  alarmSubscriptions: string[];
};

export class LambdaCronStack extends cdk.Stack {
  // arn:aws:sts::520476783531:assumed-role/RotateE2eAwsToken-RotateE2eAwsTokenLambdaServiceRo-T3JXSBHA4HOQ/RotateE2eAwsToken-RotateE2eAwsTokenLambda930F79D6
  // is not authorized to perform: sts:AssumeRole on resource: arn:aws:iam::520476783531:role/RotateE2eAwsToken-RotateE2eAwsTokenRole8F4B4F28-1H5WCWTQPSXWE
  constructor(app: cdk.App, id: string) {
    super(app, id);
    const config = fs.readJSONSync("config.json") as E2eTokenRotationConfig;

    const user = new iam.User(this, id + "User");
    const role = new iam.Role(this, id + "Role", {
      maxSessionDuration: Duration.hours(TOKEN_TTL_HOURS),
      assumedBy: new iam.AccountRootPrincipal() as iam.IPrincipal
    });
    user.addToPrincipalPolicy(
      new iam.PolicyStatement({
        resources: [role.roleArn],
        actions: ["sts:AssumeRole"],
        effect: iam.Effect.ALLOW
      })
    );
    const lambdaFn = new lambda.Function(this, id + "Lambda", {
      code: new lambda.AssetCode("lambda"),
      handler: "index.handler",
      timeout: cdk.Duration.seconds(300),
      runtime: lambda.Runtime.NODEJS_14_X
    });

    lambdaFn.role?.addToPrincipalPolicy(
      new iam.PolicyStatement({
        resources: [user.userArn],
        actions: ["iam:CreateAccessKey", "iam:DeleteAccessKey"],
        effect: iam.Effect.ALLOW
      })
    );

    lambdaFn.role?.addToPrincipalPolicy(
      new iam.PolicyStatement({
        resources: [config.circleCiToken.arn],
        actions: ["secretsmanager:GetSecretValue"],
        effect: iam.Effect.ALLOW
      })
    );

    lambdaFn.addEnvironment("TOKEN_TTL_HOURS", String(TOKEN_TTL_HOURS));
    lambdaFn.addEnvironment("E2E_ROLE_ARN", role.roleArn);
    lambdaFn.addEnvironment("E2E_USERNAME", user.userName);
    lambdaFn.addEnvironment("CIRCLECI_SLUG", config.circleCiConfig.slug);
    lambdaFn.addEnvironment(
      "CIRCLECI_CONTEXT_NAME",
      config.circleCiConfig.contextName
    );
    lambdaFn.addEnvironment(
      "CIRCLECI_SECRET_KEY_ID_VARIABLE",
      config.circleCiConfig.secretKeyIdVariableName
    );
    lambdaFn.addEnvironment(
      "CIRCLECI_SECRET_KEY_VARIABLE",
      config.circleCiConfig.secretKeyVariableName
    );
    lambdaFn.addEnvironment("SECRET_ARN", config.circleCiToken.arn);
    lambdaFn.addEnvironment("SECRET_KEY", config.circleCiToken.secretKey);

    // Although the key creation via IAM immediately returns credentials, it takes a little time
    // (on the order of ~10s) before the key is propagated widely enough to allow it to be used in an
    // sts:AssumeRole call. Unfortunately, there isn't a good way to test for the propagation other
    // than simply trying to use them, but in practice we haven't seen these become available any
    // sooner than ~8s after creation.
    lambdaFn.addEnvironment(
      "CREATE_ACCESS_KEY_TIMEOUT",
      String(CREATE_ACCESS_KEY_TIMEOUT)
    );
    const schedule = events.Schedule.expression(LAMBDA_FREQUENCY);
    const rule = new events.Rule(this, "Rule", {
      schedule
    });

    rule.addTarget(new targets.LambdaFunction(lambdaFn as any) as any);

    const topicId = "e2e_token_rotation_alarm_sns_topic";
    const topic = new sns.Topic(this, topicId);
    for (const email of config.alarmSubscriptions) {
      topic.addSubscription(new snsSubscriptions.EmailSubscription(email));
    }

    lambdaFn
      .metricErrors()
      .createAlarm(this, "e2e_token_rotation_error_alarm", {
        threshold: 1,
        evaluationPeriods: 1
      });
  }
}

const app = new cdk.App();
new LambdaCronStack(app, LAMBDA_NAME);
app.synth();
