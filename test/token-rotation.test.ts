import "@aws-cdk/assert/jest";
import * as cdk from "@aws-cdk/core";
import { LambdaCronStack } from "..";
jest.mock("fs-extra", () => {
  return {
    readJSONSync: () => ({
      circleCiToken: {
        arn:
          "arn:aws:secretsmanager:us-east-2:111111111:secret:amplify_cli_circleci_token-cawIBB",
        secretKey: "circleci-key-secret"
      },
      circleCiConfig: {
        type: "Context",
        contextName: "some-context",
        slug: "gh/someuser",
        secretKeyIdVariableName: "AWS_ACCESS_KEY_ID",
        secretKeyVariableName: "AWS_SECRET_ACCESS_KEY"
      },
      alarmSubscriptions: ["user@domain.com"]
    })
  };
});
describe("LambdaCronStack", () => {
  const app = new cdk.App();
  const stack = new LambdaCronStack(app, "mockId");

  it("should have an IAM user", () => {
    expect(stack).toHaveResource("AWS::IAM::User");
  });

  it("should use an IAM policy that allows sts:AssumeRole", () => {
    expect(stack).toHaveResourceLike("AWS::IAM::Policy", {
      PolicyDocument: {
        Statement: [
          {
            Action: "sts:AssumeRole",
            Effect: "Allow"
          }
        ]
      }
    });
  });

  it("should use an IAM role that allows sts:AssumeRole", () => {
    expect(stack).toHaveResourceLike("AWS::IAM::Role", {
      AssumeRolePolicyDocument: {
        Statement: [
          {
            Action: "sts:AssumeRole",
            Effect: "Allow"
          }
        ]
      }
    });
  });

  it("should use an IAM role that allows sts:AssumeRole for the lambda", () => {
    expect(stack).toHaveResourceLike("AWS::IAM::Role", {
      AssumeRolePolicyDocument: {
        Statement: [
          {
            Action: "sts:AssumeRole",
            Effect: "Allow",
            Principal: {
              Service: "lambda.amazonaws.com"
            }
          }
        ]
      }
    });
  });
  it("should create a policy that allows creation/deletion of a temporary access key", () => {
    expect(stack).toHaveResourceLike("AWS::IAM::Policy", {
      PolicyDocument: {
        Statement: [
          {
            Action: ["iam:CreateAccessKey", "iam:DeleteAccessKey"]
          }
        ]
      }
    });
  });
  it("should create a lambda that executes every hour", () => {
    expect(stack).toHaveResourceLike("AWS::Lambda::Function", {
      Handler: "index.handler",
      Runtime: "nodejs14.x",
      Timeout: 300
    });
    expect(stack).toHaveResourceLike("AWS::Events::Rule", {
      ScheduleExpression: "rate(1 hour)",
      State: "ENABLED"
    });
  });
});
