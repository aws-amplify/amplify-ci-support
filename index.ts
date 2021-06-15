import events = require("@aws-cdk/aws-events");
import targets = require("@aws-cdk/aws-events-targets");
import lambda = require("@aws-cdk/aws-lambda");
import iam = require("@aws-cdk/aws-iam");
import cdk = require("@aws-cdk/core");
import {config} from "dotenv";
import * as fs from "fs";
import {Duration} from "@aws-cdk/core";
const TOKEN_TTL_HOURS = 5;
const LAMBDA_FREQUENCY = "rate(1 hour)";
const LAMBDA_NAME = "RotateE2eAwsToken";
config();

export class LambdaCronStack extends cdk.Stack {
  // arn:aws:sts::520476783531:assumed-role/RotateE2eAwsToken-RotateE2eAwsTokenLambdaServiceRo-T3JXSBHA4HOQ/RotateE2eAwsToken-RotateE2eAwsTokenLambda930F79D6
  // is not authorized to perform: sts:AssumeRole on resource: arn:aws:iam::520476783531:role/RotateE2eAwsToken-RotateE2eAwsTokenRole8F4B4F28-1H5WCWTQPSXWE
  constructor(app: cdk.App, id: string) {
    super(app, id);

    const user = new iam.User(this, id + "User");
    const role = new iam.Role(this, id + "Role", {
      maxSessionDuration: Duration.hours(TOKEN_TTL_HOURS),
      assumedBy: new iam.AccountRootPrincipal() as iam.IPrincipal,
    });
    user.addToPrincipalPolicy(new iam.PolicyStatement({
      resources: [role.roleArn],
      actions: ['sts:AssumeRole'],
      effect: iam.Effect.ALLOW,
    }))
    const lambdaFn = new lambda.Function(this, id + "Lambda", {
      code: new lambda.AssetCode("lambda"),
      handler: "index.handler",
      timeout: cdk.Duration.seconds(300),
      runtime: lambda.Runtime.NODEJS_14_X,
    });

    lambdaFn.role?.addToPrincipalPolicy(new iam.PolicyStatement({
      resources: [user.userArn],
      actions: ['iam:CreateAccessKey', 'iam:DeleteAccessKey'],
      effect: iam.Effect.ALLOW,
    }))

    Object.keys(process.env).map((envName: string) => {
      if (
        fs
          .readFileSync(".env")
          .toString()
          .includes(envName)
      ) {
        const envValue = process.env[envName];
        if (!envValue || envName === "_") {
          console.log(`Not passing environment variable to lambda: ${envName}`);
          return;
        }

        console.log(`Adding environment variable: ${envName} => ${envValue}`);
        lambdaFn.addEnvironment(envName, envValue);
      }
    });

    lambdaFn.addEnvironment("TOKEN_TTL_HOURS", String(TOKEN_TTL_HOURS));
    lambdaFn.addEnvironment("E2E_ROLE_ARN", role.roleArn);
    lambdaFn.addEnvironment("E2E_USERNAME", user.userName);
    const schedule = events.Schedule.expression(LAMBDA_FREQUENCY);
    const rule = new events.Rule(this, "Rule", {
      schedule,
    });

    rule.addTarget(new targets.LambdaFunction(lambdaFn as any) as any);
  }
}

const app = new cdk.App();
new LambdaCronStack(app, LAMBDA_NAME);
app.synth();
