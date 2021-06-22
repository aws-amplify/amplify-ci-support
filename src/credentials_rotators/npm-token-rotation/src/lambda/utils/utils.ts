import aws from "aws-sdk";
import assert from "assert";
import Ajv from "ajv";
import * as fs from "fs";
import {
  NPMTokenRotationConfig,
  AccessTokenItem,
  SecretDetail,
} from "../../stacks/types";

import { schema } from "./config-schema";
import axios from "axios";

export type NPMCredentials = {
  username: string;
  password: string;
  otpSeed: string;
};

/**
 * Gets an instance of SecretsManager client
 * @returns SecretsManager
 */
export const getSecretsManagerClient = async (
  region?: string,
  roleArn?: string
): Promise<aws.SecretsManager> => {
  let config: aws.ConfigurationOptions = {};
  if (roleArn) {
    const assumedRole = await new aws.STS()
      .assumeRole({
        RoleArn: roleArn,
        RoleSessionName: `getSecrets`,
        DurationSeconds: 900,
      })
      .promise();
    const assumedRoleCredentials = assumedRole.Credentials!;
    config.credentials = {
      accessKeyId: assumedRoleCredentials.AccessKeyId,
      secretAccessKey: assumedRoleCredentials.SecretAccessKey,
      sessionToken: assumedRoleCredentials.SessionToken,
    };
  }
  config.region = region;
  return new aws.SecretsManager(config);
};

/**
 * Get NPM credentials from secrets manager
 * @param options details like clientRequestToken and stage
 * @returns credentials
 */
export const getCredentials = async (
  config: NPMTokenRotationConfig,
  options: { ClientRequestToken?: string; stage?: string } = {}
): Promise<NPMCredentials> => {
  console.info("start:getCredentials");
  const userNameArn = config.npmLoginUsernameSecret.arn;
  const userNameKey = config.npmLoginUsernameSecret.secretKey;
  const userNameRoleArn = config.npmLoginUsernameSecret.roleArn;
  assert(userNameArn, "config is missing  variable npmLoginUsernameSecret.arn");
  assert(
    userNameKey,
    "config is missing variable npmLoginUsernameSecret.secretKey"
  );
  const username = await getSecret(
    userNameArn,
    userNameKey,
    userNameRoleArn,
    options
  );

  const passwordArn = config.npmLoginPasswordSecret.arn;
  const passwordKey = config.npmLoginPasswordSecret.secretKey;
  const passwordRoleArn = config.npmLoginPasswordSecret.roleArn;
  assert(passwordArn, "config.npmLoginPasswordSecret.arn missing");
  assert(passwordKey, "config.npmLoginPasswordSecret.secretKey missing");
  const password = await getSecret(
    passwordArn,
    passwordKey,
    passwordRoleArn,
    options
  );

  const otpSeedArn = config.npmOtpSeedSecret.arn;
  const optSeedKey = config.npmOtpSeedSecret.secretKey;
  const otpSecretRoleArn = config.npmOtpSeedSecret.roleArn;
  assert(otpSeedArn, "config.npmOtpSeedSecret.arn missing");
  assert(optSeedKey, "config.npmOtpSeedSecret.secretKey missing");
  const otpSeed = await getSecret(
    otpSeedArn,
    optSeedKey,
    otpSecretRoleArn,
    options
  );
  console.info("end:getCredentials");

  return { username, password, otpSeed };
};

/**
 *
 * @param arn arn of the secret that the value should be retrieved from
 * @param key value in the secret
 * @param options Additional options like clientRequest token and stage
 * @returns string
 */
export const getSecret = async (
  arn: string,
  key: string,
  roleArn?: string,
  options: { ClientRequestToken?: string; stage?: string } = {}
) => {
  console.info(`start:getSecret()`);
  const requestOptions = {
    VersionStage: options.stage,
    VersionId: options.ClientRequestToken,
  };
  const region = arn.split(":")[3];
  const secretsManager = await getSecretsManagerClient(region, roleArn);

  const secret = await secretsManager
    .getSecretValue({
      ...requestOptions,
      SecretId: arn.trim(),
    })
    .promise();
  const data = JSON.parse(secret.SecretString!);
  console.info(`end:getSecret()`);
  return data[key];
};

export const getTokenConfigForArn = (
  config: NPMTokenRotationConfig,
  arn: string
): AccessTokenItem => {
  console.info("begin: getTokenConfigForArn");
  const tokenDetails = config.npmAccessTokenSecrets.secrets.find(
    (s) => s.arn === arn
  );
  if (!tokenDetails) {
    throw new Error(
      `Invalid configuration. Configuration is missing for arn ${arn}`
    );
  }
  console.info("end: getTokenConfigForArn");
  return tokenDetails;
};

export const loadConfiguration = async (
  configFile: string
): Promise<NPMTokenRotationConfig> => {
  const content = fs.readFileSync(configFile, { encoding: "utf-8" });
  const config = JSON.parse(content);
  await validateConfiguration(config);
  return config as NPMTokenRotationConfig;
};

export const sendSlackMessage = async (webhookUrl: string, message: string) => {
  assert(webhookUrl, "webhook url is missing");
  assert(message, "message is missing");
  await axios.post(webhookUrl, {
    message,
  });
};

export const validateConfiguration = async (payload: any) => {
  const a = new Ajv();
  const validator = a.compile(schema);
  const result = validator(payload);
  if (!result) {
    console.log("Configuration validation failed");
    throw new Error("Configuration validation failed");
  }
  const validatedJson = payload as NPMTokenRotationConfig;
  await assertSecretAccess(
    validatedJson.npmLoginUsernameSecret,
    "npmLoginUserNameSecret is not accessible"
  );
  await assertSecretAccess(
    validatedJson.npmLoginPasswordSecret,
    "npmLoginPasswordSecret is not accessible"
  );

  await assertSecretAccess(
    validatedJson.npmOtpSeedSecret,
    "npmOtpSeedSecret is not accessible"
  );
  
  return result;
};

export const assertSecretAccess = async (
  secretConfig: SecretDetail,
  message: string
): Promise<void> => {
  try {
    getSecret(secretConfig.arn, secretConfig.secretKey, secretConfig.roleArn);
  } catch (e) {
    console.log(e);
    const error = new Error(message);
    throw error;
  }
};
