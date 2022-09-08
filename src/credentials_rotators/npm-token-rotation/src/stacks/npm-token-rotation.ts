import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as lambdaNodeJs from "aws-cdk-lib/aws-lambda-nodejs";
import * as sfn from "aws-cdk-lib/aws-stepfunctions";
import * as tasks from "aws-cdk-lib/aws-stepfunctions-tasks";
import { IFunction } from "aws-cdk-lib/aws-lambda";
import * as path from "path";

import { NPMTokenRotationConfig } from "../config-types";
import { BaseStack } from "./base-stack";
import { Duration } from "aws-cdk-lib";

export type NpmTokenRotationStackParams = {
  config: NPMTokenRotationConfig;
};

export class NpmTokenRotationStack extends BaseStack {
  private secretConfig: NPMTokenRotationConfig;

  constructor(
    scope: Construct,
    id: string,
    options: NpmTokenRotationStackParams
  ) {
    super(scope, id);
    this.secretConfig = options.config;

    /**
     * Secrets manger rotation lambda
     * https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_how.html
     */
    const rotatorFn = new lambdaNodeJs.NodejsFunction(this, "lambda", {
      timeout: Duration.seconds(10),
      entry: path.join(__dirname, "../lambda/create-new-token/index.ts"),
    });

    const { tokenPublisherFn, tokenRemovalFn } = this.getStepFunctions();

    /**
     * This state machine publishes new token to GitHub, waits 15 minutes, and
     * removes old token on NPM.
     */
    const publishNewTokenStateMachine = this.buildTokenPublishStateMachine(
      Duration.minutes(15),
      tokenPublisherFn,
      tokenRemovalFn
    );

    // This will be referenced by rotation lambda.
    this.addEnvironment(
      "PUBLISH_TOKEN_STATE_MACHINE_ARN",
      publishNewTokenStateMachine.stateMachineArn,
      [rotatorFn]
    );

    this.grantLambdaResourcePermissions(
      rotatorFn,
      tokenPublisherFn,
      tokenRemovalFn,
      publishNewTokenStateMachine
    );

    this.enableLambdaCloudWatchAlarms(
      rotatorFn,
      tokenPublisherFn,
      tokenRemovalFn
    );
  }

  private grantLambdaResourcePermissions(
    rotatorFn: lambdaNodeJs.NodejsFunction,
    tokenPublisherFn: lambdaNodeJs.NodejsFunction,
    tokenRemovalFn: lambdaNodeJs.NodejsFunction,
    publishNewTokenStateMachine: sfn.StateMachine
  ) {
    this.grantSecretsManagerToAccessLambda(rotatorFn);

    this.grantLambdaFunctionToAccessStepFunctions(
      rotatorFn,
      publishNewTokenStateMachine
    );

    this.grantLambdaAccessToSecrets(rotatorFn, [
      this.secretConfig.npmLoginUsernameSecret,
      this.secretConfig.npmLoginPasswordSecret,
      this.secretConfig.npmOtpSeedSecret,
    ]);
    this.grantLambdaAccessToSecrets(tokenRemovalFn, [
      this.secretConfig.npmLoginUsernameSecret,
      this.secretConfig.npmLoginPasswordSecret,
      this.secretConfig.npmOtpSeedSecret,
    ]);

    for (const token of this.secretConfig.npmAccessTokenSecrets.secrets) {
      this.grantLambdaAccessToRotateSecrets(rotatorFn, token);
      this.grantLambdaAccessToSecrets(tokenRemovalFn, [
        token,
        ...(token.slackWebHookConfig ? [token.slackWebHookConfig] : []),
      ]);
      this.grantLambdaAccessToSecrets(tokenPublisherFn, [
        token,
        token.publishConfig.githubToken,
        ...(token.slackWebHookConfig ? [token.slackWebHookConfig] : []),
      ]);
      this.configureSecretRotation(rotatorFn, token, Duration.days(1));
    }
  }

  private enableLambdaCloudWatchAlarms(
    rotatorFn: lambdaNodeJs.NodejsFunction,
    tokenPublisherFn: lambdaNodeJs.NodejsFunction,
    tokenRemovalFn: lambdaNodeJs.NodejsFunction
  ) {
    this.enableCloudWatchAlarmNotification(
      rotatorFn,
      "npm_access_token_secrets",
      this.secretConfig.npmAccessTokenSecrets
    );
    this.enableCloudWatchAlarmNotification(
      tokenPublisherFn,
      "token_publisher",
      this.secretConfig.npmAccessTokenSecrets
    );
    this.enableCloudWatchAlarmNotification(
      tokenRemovalFn,
      "token_remover",
      this.secretConfig.npmAccessTokenSecrets
    );
  }

  private buildTokenPublishStateMachine = (
    wait: Duration,
    publishFn: IFunction,
    deleteFn: IFunction
  ): sfn.StateMachine => {
    wait.formatTokenToNumber();
    const steps = new tasks.LambdaInvoke(this, "publish-new-token", {
      lambdaFunction: publishFn,
      payloadResponseOnly: true,
    })
      .next(
        new sfn.Wait(
          this,
          `Wait ${wait.toHumanString()} before invalidating NPM Access Token`,
          { time: sfn.WaitTime.duration(wait) }
        )
      )
      .next(
        new tasks.LambdaInvoke(this, "invalidate-old-token", {
          lambdaFunction: deleteFn,
          payloadResponseOnly: true,
          timeout: wait.plus(Duration.minutes(1)),
        })
      );

    return new sfn.StateMachine(this, "publish-new-token-step-fn", {
      definition: steps,
    });
  };

  private getStepFunctions() {
    const tokenPublisherFn = new lambdaNodeJs.NodejsFunction(
      this,
      "step-fn-token-publisher",
      {
        entry: path.join(__dirname, "../lambda/step-01-publish-token/index.ts"),
        timeout: Duration.seconds(10),
      }
    );

    const tokenRemovalFn = new lambdaNodeJs.NodejsFunction(
      this,
      "step-fn-delete-token",
      {
        entry: path.join(
          __dirname,
          "../lambda/step-02-delete-old-token/index.ts"
        ),
        timeout: Duration.seconds(10),
      }
    );
    return { tokenPublisherFn, tokenRemovalFn };
  }

  private addEnvironment(name: string, value: string, fns: lambda.Function[]) {
    for (const fn of fns) {
      fn.addEnvironment(name, value);
    }
  }
}
