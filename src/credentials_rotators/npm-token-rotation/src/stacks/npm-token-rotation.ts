import * as core from "@aws-cdk/core";
import * as lambda from "@aws-cdk/aws-lambda";
import * as lambdaNodeJs from "@aws-cdk/aws-lambda-nodejs";
import * as sfn from "@aws-cdk/aws-stepfunctions";
import * as tasks from "@aws-cdk/aws-stepfunctions-tasks";
import * as path from "path";

import { BaseStack } from "./base-stack";
import { NPMTokenRotationConfig } from "./types";
import { Duration } from "@aws-cdk/core";
import { IFunction } from "@aws-cdk/aws-lambda";

export type NpmTokenRotationStackParams = {
  config: NPMTokenRotationConfig;
};
export class NpmTokenRotationStack extends BaseStack {
  private secretConfig: NPMTokenRotationConfig;

  constructor(
    scope: core.Construct,
    id: string,
    options: NpmTokenRotationStackParams
  ) {
    super(scope, id);
    this.secretConfig = options.config;
    const rotatorFn = new lambdaNodeJs.NodejsFunction(this, "lambda", {
      entry: path.normalize(
        path.join(__dirname, "..", "lambda", "create-new-token", "index.ts")
      ),
    });

    const tokenPublisherFn = new lambdaNodeJs.NodejsFunction(
      this,
      "step-fn-token-publisher",
      {
        entry: path.normalize(
          path.join(
            __dirname,
            "..",
            "lambda",
            "step-01-publish-token",
            "index.ts"
          )
        ),
      }
    );
    const githubTokenWriteFn = new lambdaNodeJs.NodejsFunction(
      this,
      "step-fn-github-token-write",
      {
        entry: path.normalize(
          path.join(
            __dirname,
            "..",
            "lambda",
            "step-02-github-repo-write",
            "index.ts"
          )
        ),
      }
    )

    const tokenRemovalFn = new lambdaNodeJs.NodejsFunction(
      this,
      "step-fn-delete-token",
      {
        entry: path.normalize(
          path.join(
            __dirname,
            "..",
            "lambda",
            "step-03-delete-old-token",
            "index.ts"
          )
        ),
      }
    );

    const deleteOldTokenStateMachine = this.buildTokenDeletionStateMachine(
      core.Duration.minutes(15),
      tokenPublisherFn,
      githubTokenWriteFn,
      tokenRemovalFn
    );

    this.addEnvironment(
      "DELETE_TOKEN_STATE_MACHINE_ARN",
      deleteOldTokenStateMachine.stateMachineArn,
      [rotatorFn]
    );

    this.grantSecretsManagerToAccessLambda(rotatorFn);

    this.grantLambdaFunctionToAccessStepFunctions(
      rotatorFn,
      deleteOldTokenStateMachine
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
        token.publishConfig.circleCiToken,
        ...(token.slackWebHookConfig ? [token.slackWebHookConfig] : []),
      ]);
      this.grantLambdaAccessToSecrets(githubTokenWriteFn, [token, token.publishConfig.githubToken])
      this.configureSecretRotation(rotatorFn, token, Duration.days(7));
    }

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
      tokenPublisherFn,
      "token_remover",
      this.secretConfig.npmAccessTokenSecrets
    );
  }

  private buildTokenDeletionStateMachine = (
    wait: core.Duration,
    publishFn: IFunction,
    githubWrite: IFunction,
    deleteFn: IFunction
  ): sfn.StateMachine => {
    wait.formatTokenToNumber();
    const steps = new tasks.LambdaInvoke(this, "publish-new-token", {
      lambdaFunction: publishFn,
      payloadResponseOnly: true,
    })
    .next(
      new tasks.LambdaInvoke(this, "github-repo-write", {
        lambdaFunction: githubWrite,
        payloadResponseOnly: true,
      })
    )
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

    return new sfn.StateMachine(this, "token-invalidation-step-fn", {
      definition: steps,
    });
  };

  private addEnvironment = (
    name: string,
    value: string,
    fns: lambda.Function[]
  ) => {
    for (const fn of fns) {
      fn.addEnvironment(name, value);
    }
  };
}
