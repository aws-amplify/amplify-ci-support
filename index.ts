import events = require("@aws-cdk/aws-events");
import targets = require("@aws-cdk/aws-events-targets");
import { NodejsFunction } from "@aws-cdk/aws-lambda-nodejs";
import iam = require("@aws-cdk/aws-iam");
import sns = require("@aws-cdk/aws-sns");
import snsSubscriptions = require("@aws-cdk/aws-sns-subscriptions");
import cdk = require("@aws-cdk/core");
import { Duration } from "@aws-cdk/core";
import * as path from "path";
import {
  E2eTokenRotationConfig,
  loadConfiguration
} from "./lambda/utils/validateConfiguration";
import { CircleCiConfig } from "./lambda/utils/updateCircleCiEnvironmentVariable";

// This is 1 hour (lambda rotation frequency) plus an additional 7 hours for test steps to run.
// Currently the full e2e suite takes <4 hours, so this should be plenty of buffer time
// without sacrificing the security of the token being short-lived
const TOKEN_TTL_HOURS = 8;
const LAMBDA_FREQUENCY = "rate(1 hour)";
const LAMBDA_NAME = "RotateE2eAwsToken";
const CREATE_ACCESS_KEY_TIMEOUT = 10000;
export class LambdaCronStack extends cdk.Stack {
  constructor(app: cdk.App, id: string) {
    super(app, id);
    const config = loadConfiguration(
      path.join(__dirname, "config.json")
    ) as E2eTokenRotationConfig;

    const user = new iam.User(this, id + "User");

    const lambdaFn = new NodejsFunction(this, id + "Lambda", {
      entry: path.normalize(path.join(__dirname, ".", "lambda", "index.ts")),
      timeout: Duration.minutes(5)
    });

    const getPolicyStatements = (circleCiConfig: CircleCiConfig) => {
      return circleCiConfig.permissions.map(
        permission =>
          new iam.PolicyStatement({
            resources: permission.resources,
            actions: permission.actions,
            effect:
              permission.effect.toLowerCase() === "allow"
                ? iam.Effect.ALLOW
                : iam.Effect.DENY
          })
      );
    };

    config.circleCiConfigs.forEach(circleCiConfig => {
      const role = new iam.Role(this, id + circleCiConfig.roleName + "Role", {
        roleName: `${id}-${circleCiConfig.roleName}`,
        inlinePolicies: {
          roleNamePolicy: new iam.PolicyDocument({
            statements: getPolicyStatements(circleCiConfig)
          })
        },
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

      lambdaFn.role?.addToPrincipalPolicy(
        new iam.PolicyStatement({
          resources: [role.roleArn],
          actions: ["iam:GetRole"],
          effect: iam.Effect.ALLOW
        })
      );
    });

    lambdaFn.role?.addToPrincipalPolicy(
      new iam.PolicyStatement({
        resources: [user.userArn],
        actions: [
          "iam:CreateAccessKey",
          "iam:DeleteAccessKey",
          "iam:ListAccessKeys"
        ],
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
    lambdaFn.addEnvironment("E2E_USERNAME", user.userName);
    lambdaFn.addEnvironment("ROLE_PREFIX", `${id}-`);

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
