import config from "../../../config.json";
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
        tokenDetails.slackWebHookConfig.secretKey,
        tokenDetails.slackWebHookConfig.roleArn
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
        tokenConfig.secretKey,
        tokenConfig.roleArn
      );
      if (!circleCIToken) {
        throw new Error("Could not get the CircleCI token");
      }
      const newNPMToken = await utils.getSecret(
        event.secretArn,
        tokenDetails.secretKey,
        tokenDetails.roleArn
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
      } else if (tokenDetails.publishConfig.type === "Environment") {
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
      } else {
        throw new Error("Invalid publishConfig");
      }

      await updateCircleCIEnvironmentVariables(circleCIToken, updateConfig);
      if (webhookUrl) {
        const repoUserName = tokenDetails.publishConfig.slug.replace("gh/", "");
        const message =
          tokenDetails.publishConfig.type === "Context"
            ? `NPM Publish Token has been rotated and pushed to CircleCI Context.\nDetails:\n ${JSON.stringify(
                {
                  contextName: tokenDetails.publishConfig.contextName,
                  variableName: tokenDetails.publishConfig.variableName,
                  org: repoUserName,
                }
              )}`
            : `NPM Publish Token has been rotated and Stored in Environment. \nDetails: \n ${JSON.stringify(
                {
                  projectName: tokenDetails.publishConfig.projectName,
                  variableName: tokenDetails.publishConfig.variableName,
                  org: repoUserName,
                }
              )}`;
        await utils.sendSlackMessage(webhookUrl, message);
      }
    } catch (e) {
      if (webhookUrl) {
        await utils.sendSlackMessage(
          webhookUrl,
          `NPM Access token rotation failed. Runbook: https://tiny.amazon.com/rv8519a6 Error: ${e}`,
        );
      }
      throw e;
    }
  }
  return event;
};
