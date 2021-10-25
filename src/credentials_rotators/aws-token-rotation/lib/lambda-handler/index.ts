import * as aws from "aws-sdk";
import { updateGithubEnvironmentSecret } from "../../../common-utils/github-helper";
export async function handler(_: any, context: any) {
  const { CROSS_ACCOUNT_ROLE_ARN, ROLE_ARN, GITHUB_TOKEN_ARN } = process.env;
  const sts = new aws.STS();
  console.assert(CROSS_ACCOUNT_ROLE_ARN, "ROLE_ARN should have value");
  // assuming role of the other account
  const assumeRoleResult = await sts
    .assumeRole({
      RoleArn: CROSS_ACCOUNT_ROLE_ARN || "",
      RoleSessionName: "export-test-role",
    })
    .promise();
  const creds = assumeRoleResult.Credentials;


  const iam = new aws.IAM({
    credentials: {
      accessKeyId: creds?.AccessKeyId || "",
      secretAccessKey: creds?.SecretAccessKey || "",
      sessionToken: creds?.SessionToken || "",
    },
  });

  // getting the keys of the user
  const accessKeys = await iam
    .createAccessKey({
      UserName: "amplify-cli-export-user",
    })
    .promise();

  if (!assumeRoleResult.Credentials) {
    throw new Error("Unable to get keys");
  }
  const { AccessKeyId, SecretAccessKey } = accessKeys.AccessKey;

  await sleep(10000);

  const crossSts = new aws.STS({
    accessKeyId: AccessKeyId,
    secretAccessKey: SecretAccessKey,
  });

  // using the keys of the other role
  console.assert(ROLE_ARN, "ROLE_ARN should have value");
  const crossAccountAssumeRoleResult = await crossSts
    .assumeRole({
      RoleArn: ROLE_ARN || "",
      RoleSessionName: "export-test-role",
      DurationSeconds: 6 * 60 * 60,
    })
    .promise();

  // writing github keys
  console.assert(GITHUB_TOKEN_ARN, "GITHUB_TOKEN_ARN should have value");

  const sm = new aws.SecretsManager();

  const val = await sm
    .getSecretValue({ SecretId: GITHUB_TOKEN_ARN || "" })
    .promise();
  
  const githubConfig = {
    owner: "aws-amplify",
    repo: "amplify-cli-export-construct",
    token: val.SecretString || "",
  };

  await updateGithubEnvironmentSecret(
    githubConfig,
    crossAccountAssumeRoleResult.Credentials?.AccessKeyId || "",
    "AWS_ACCESS_KEY_ID"
  );
  await updateGithubEnvironmentSecret(
    githubConfig,
    crossAccountAssumeRoleResult.Credentials?.SecretAccessKey || "",
    "AWS_SECRET_ACCESS_KEY"
  );
  await updateGithubEnvironmentSecret(
    githubConfig,
    crossAccountAssumeRoleResult.Credentials?.SessionToken || "",
    "AWS_SESSION_TOKEN"
  );

  //delete keys

  await iam
    .deleteAccessKey({
      AccessKeyId,
      UserName: 'amplify-cli-export-user',
    })
    .promise();

    return context;
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
