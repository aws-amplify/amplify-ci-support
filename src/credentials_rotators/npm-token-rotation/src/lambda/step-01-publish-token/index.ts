import config from "../../../secret_config.json";
import assert from "assert";
import {
  ContextVariables,
  EnvironmentVariables,
  updateCircleCIEnvironmentVariables,
} from "../utils/circleci-helper";
import * as utils from "../utils/utils";
import {
  NPMTokenRotationConfig,
  TokenPublishCircleCIEnvironmentConfig,
  TokenRotationStepFnEvent,
} from "../../stacks/types";

export const handler = async (event: TokenRotationStepFnEvent) => {
  const tokenDetails = utils.getTokenConfigForArn(
    config as NPMTokenRotationConfig,
    event.secretArn
  );
  const webhookUrl = tokenDetails.slackWebHookConfig
    ? await utils.getSecret(
        tokenDetails.slackWebHookConfig.arn,
        tokenDetails.slackWebHookConfig.secretKey
      )
    : undefined;
  if (tokenDetails) {
    try {
      const tokenConfig = tokenDetails.publishConfig.circleCiToken;
      if (!tokenConfig || !tokenConfig.arn || !tokenConfig.secretKey) {
        throw Error(
          `Invalid rotation configuration. Expected arn and token key, got ${JSON.stringify(
            tokenConfig
          )}`
        );
      }
      const circleCIToken = await utils.getSecret(
        tokenConfig.arn,
        tokenConfig.secretKey
      );
      if (!circleCIToken) {
        throw new Error("Could not get the CircleCI token");
      }
      const newNPMToken = await utils.getSecret(
        event.secretArn,
        tokenDetails.secretKey
      );
      assert(newNPMToken, "Secret manager should have newNPMToken");

      let updateConfig: ContextVariables | EnvironmentVariables;
      if (tokenDetails.publishConfig.type === "Context") {
        updateConfig = {
          type: tokenDetails.publishConfig.type,
          context: tokenDetails.publishConfig.contextName!,
          slug: tokenDetails.publishConfig.slug,
          variables: {
            [tokenDetails.publishConfig.variableName]: newNPMToken,
          },
        };
      } else {
        assert(
          (tokenDetails.publishConfig as TokenPublishCircleCIEnvironmentConfig)
            .projectName,
          "Project name is missing"
        );
        updateConfig = {
          type: "Environment",
          slug: tokenDetails.publishConfig.slug,
          variables: {
            [tokenDetails.publishConfig.variableName]: newNPMToken,
          },
          projectName: (
            tokenDetails.publishConfig as TokenPublishCircleCIEnvironmentConfig
          ).projectName,
        };
      }

      await updateCircleCIEnvironmentVariables(circleCIToken, updateConfig);
      if (webhookUrl) {
        const message =
          tokenDetails.publishConfig.type === "Context"
            ? `NPM Token has been rotated and pushed to ${tokenDetails.publishConfig.contextName} and stored with ENV Variable name ${tokenDetails.publishConfig.variableName}`
            : `NPM Token has been rotated and stored under ENV variable name ${tokenDetails.publishConfig.variableName} in project ${tokenDetails.publishConfig.projectName}`;
        await utils.sendSlackMessage(webhookUrl, message);
      }
    } catch (e) {
      if (webhookUrl) {
        await utils.sendSlackMessage(
          webhookUrl,
          "NPM Access token has been rotation failed"
        );
      }
      throw e;
    }
  }
  return event;
};
