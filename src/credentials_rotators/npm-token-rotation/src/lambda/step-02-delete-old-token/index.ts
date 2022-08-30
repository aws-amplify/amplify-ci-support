import { deleteAccessToken } from "../utils/npm-utils";
import {
  getCredentials,
  getSecret,
  getTokenConfigForArn,
  sendSlackMessage,
} from "../utils/utils";
import config from "../../../config.json";
import {
  NPMTokenRotationConfig,
  TokenRotationStepFnEvent,
} from "../../stacks/types";

export const handler = async (event: TokenRotationStepFnEvent) => {
  console.info(`start: handler(${JSON.stringify(event)})`);
  const npmCredentials = await getCredentials(
    config as unknown as NPMTokenRotationConfig
  );
  const tokenConfig = getTokenConfigForArn(
    config as NPMTokenRotationConfig,
    event.secretArn
  );

  const tokenToDelete = await getSecret(
    event.secretArn,
    tokenConfig.secretKey,
    tokenConfig.roleArn,
    {
      ClientRequestToken: event.tokenEvent,
    }
  );

  const tokenDetails = getTokenConfigForArn(
    config as NPMTokenRotationConfig,
    event.secretArn
  );
  const webhookUrl = tokenDetails.slackWebHookConfig
    ? await getSecret(
        tokenDetails.slackWebHookConfig.arn,
        tokenDetails.slackWebHookConfig.secretKey,
        tokenDetails.slackWebHookConfig.roleArn
      )
    : undefined;

  try {
    await deleteAccessToken(
      npmCredentials.username,
      npmCredentials.password,
      npmCredentials.otpSeed,
      tokenToDelete
    );
    console.info(`end: handler(${JSON.stringify(event)})`);
  } catch (e) {
    if (webhookUrl) {
      sendSlackMessage(webhookUrl, `Deleting the old NPM token failed: ${e}`);
    }
    throw e;
  }
  return event;
};
