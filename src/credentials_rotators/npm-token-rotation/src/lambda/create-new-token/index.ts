import { createAccessToken, validateAccessToken } from "../utils/npm-utils";
import aws from "aws-sdk";
import assert from "assert";
import {
  getSecret,
  getSecretsManagerClient,
  getCredentials,
  NPMCredentials,
  getTokenConfigForArn,
} from "../utils/utils";

import config from "../../../config.json";
import { AccessTokenItem, NPMTokenRotationConfig } from "../../config-types";

export type SecretRotationEvent = {
  SecretId: string;
  ClientRequestToken: string;
  Step: "createSecret" | "setSecret" | "testSecret" | "finishSecret";
};

const setSecret = (
  event: SecretRotationEvent,
  credential: NPMCredentials,
  tokenConfig: AccessTokenItem
) => {
  console.info("setSecret: Skip the step as no action necessary");
};

const testSecret = async (
  event: SecretRotationEvent,
  credential: NPMCredentials,
  tokenConfig: AccessTokenItem
) => {
  console.info(`start:testSecret()`);
  const stagedToken = await getSecret(
    event.SecretId,
    tokenConfig.secretKey,
    undefined,
    {
      ClientRequestToken: event.ClientRequestToken,
      stage: "AWSPENDING",
    }
  );
  await validateAccessToken(credential.username, stagedToken);
  console.info("testSecret: Successfully tested secret");
  console.info(`end:testSecret()`);
};

const finishSecret = async (
  event: SecretRotationEvent,
  credentials: NPMCredentials,
  tokenConfig: AccessTokenItem
) => {
  console.info(`start:finishSecret()`);

  const secretsManagerClient = await getSecretsManagerClient();
  const metadata = await secretsManagerClient
    .describeSecret({ SecretId: event.SecretId })
    .promise();

  const currentVersion = Object.keys(metadata.VersionIdsToStages ?? {}).find(
    versionId => {
      return metadata.VersionIdsToStages![versionId].includes("AWSCURRENT");
    }
  );

  assert(currentVersion, "Secret should have current version");
  if (currentVersion === event.ClientRequestToken) {
    console.info(
      `finishSecret: Version ${event.ClientRequestToken} already marked as AWSCURRENT`
    );
    return;
  }

  const stepFnClient = new aws.StepFunctions();
  const stepFnArn = process.env.PUBLISH_TOKEN_STATE_MACHINE_ARN;
  assert(stepFnArn, "Missing PUBLISH_TOKEN_STATE_MACHINE_ARN env variable");

  const stepFnPayload = {
    tokenEvent: currentVersion,
    secretArn: event.SecretId,
  };

  await stepFnClient
    .startExecution({
      stateMachineArn: stepFnArn,
      input: JSON.stringify(stepFnPayload),
    })
    .promise();

  await secretsManagerClient
    .updateSecretVersionStage({
      SecretId: event.SecretId,
      VersionStage: "AWSCURRENT",
      MoveToVersionId: event.ClientRequestToken,
      RemoveFromVersionId: currentVersion,
    })
    .promise();

  console.info(`end:finishSecret()`);
};

const createSecret = async (
  event: SecretRotationEvent,
  credentials: NPMCredentials,
  tokenConfig: AccessTokenItem
) => {
  console.info(`start:createSecret()`);
  // check if there is already a credential that is pending
  try {
    await getSecret(event.SecretId, tokenConfig.secretKey, undefined, {
      ClientRequestToken: event.ClientRequestToken,
      stage: "AWSPENDING",
    });
    console.info(`Secret already is in AWSPENDING. Not creating a new one`);
  } catch (e) {
    if ((e as aws.AWSError).code === "ResourceNotFoundException") {
      const secretsManagerClient = await getSecretsManagerClient();
      console.info("Requesting a new npm access token");

      const newToken = await createAccessToken(
        credentials.username,
        credentials.password,
        credentials.otpSeed
      );
      await secretsManagerClient
        .putSecretValue({
          SecretId: event.SecretId,
          ClientRequestToken: event.ClientRequestToken,
          VersionStages: ["AWSPENDING"],
          SecretString: JSON.stringify({ [tokenConfig.secretKey]: newToken }),
        })
        .promise();
      console.info("createSecret: Successfully put secret");
    } else {
      throw e;
    }
  }
  console.info(`end:createSecret()`);
};

/**
 * Checks the current status of the Secret and throws error if no rotation is needed
 * @param secretArn Arn of the secret that is being rotated
 * @param clientRequestToken clientRequestToken for the rotation
 */
const assertRotationStatus = async (
  secretArn: string,
  clientRequestToken: string
) => {
  console.info(`start:assertRotationStatus()`);
  const secretsMetadata = await (await getSecretsManagerClient())
    .describeSecret({ SecretId: secretArn })
    .promise();
  if (!secretsMetadata.RotationEnabled) {
    console.error(`Secret ${secretArn} is not enabled for rotation`);
    throw new Error("Secret ${secretArn} is not enabled for rotation");
  }
  const versions = secretsMetadata.VersionIdsToStages;
  if (!versions || !versions[clientRequestToken]) {
    console.error(`Secret ${secretArn} has no stage for rotation of secret.`);
    throw new Error(`Secret ${secretArn} has no stage for rotation of secret.`);
  }
  console.info(`end:assertRotationStatus()`);
};

export const handler = async (event: SecretRotationEvent) => {
  console.info(`start:handler()`);
  await assertRotationStatus(event.SecretId, event.ClientRequestToken);
  const tokenConfig = getTokenConfigForArn(
    config as unknown as NPMTokenRotationConfig,
    event.SecretId
  );
  assert(tokenConfig, "Token configuration is missing");
  const npmCredentials = await getCredentials(
    config as unknown as NPMTokenRotationConfig
  );
  switch (event.Step) {
    case "createSecret":
      await createSecret(event, npmCredentials, tokenConfig);
      break;
    case "setSecret":
      await setSecret(event, npmCredentials, tokenConfig);
      break;
    case "testSecret":
      await testSecret(event, npmCredentials, tokenConfig);
      break;
    case "finishSecret":
      await finishSecret(event, npmCredentials, tokenConfig);
      break;
  }
  console.info(`end:handler())`);
};
