import { getSecret, getTokenConfigForArn, sendSlackMessage } from '../utils/utils'
import * as config from '../../../secret_config.json';
import { NPMTokenRotationConfig } from '../../stacks/types';
export const handler = async (event: RotationE) => {
  const tokenDetails = getTokenConfigForArn(
    config as NPMTokenRotationConfig,
    event.secretArn
  );
  const webhookUrl = tokenDetails.slackWebHookConfig
    ? await getSecret(
        tokenDetails.slackWebHookConfig.arn,
        tokenDetails.slackWebHookConfig.secretKey
      )
    : undefined;

}